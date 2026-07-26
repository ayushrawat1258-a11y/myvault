import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.utils import platform

import crypto_utils
from android_bridge import authenticate_fingerprint, pick_image

VAULT_ROOT_NAME = "vault_data"


class LockScreen(Screen):
    def on_enter(self):
        # Fires the moment the black screen appears — no button tap needed,
        # just touch the fingerprint sensor once.
        self.ids.status_label.text = ""
        Clock.schedule_once(lambda dt: self.try_unlock(), 0.3)

    def try_unlock(self):
        self.ids.status_label.text = ""
        authenticate_fingerprint(self.unlock_success, self.unlock_error)

    def unlock_success(self):
        Clock.schedule_once(lambda dt: setattr(self.manager, "current", "home"), 0)

    def unlock_error(self, message):
        Clock.schedule_once(lambda dt: setattr(self.ids.status_label, "text", message), 0)


class HomeScreen(Screen):
    def on_enter(self):
        self.refresh_folders()

    def refresh_folders(self):
        container = self.ids.folder_list
        container.clear_widgets()
        vault_root = App.get_running_app().vault_root
        for name in sorted(os.listdir(vault_root)):
            full = os.path.join(vault_root, name)
            if os.path.isdir(full):
                btn = Button(text=name, size_hint_y=None, height=56)
                btn.bind(on_release=lambda inst, n=name: self.open_folder(n))
                container.add_widget(btn)

    def open_folder(self, name):
        folder_screen = self.manager.get_screen("folder")
        folder_screen.folder_name = name
        self.manager.current = "folder"

    def new_folder_popup(self):
        box = BoxLayout(orientation="vertical", spacing=10, padding=10)
        inp = TextInput(hint_text="Folder name", multiline=False)
        btn = Button(text="Create", size_hint_y=None, height=48)
        box.add_widget(inp)
        box.add_widget(btn)
        popup = Popup(title="New folder", content=box, size_hint=(0.8, 0.4))

        def create(_):
            name = inp.text.strip()
            if name:
                path = os.path.join(App.get_running_app().vault_root, name)
                os.makedirs(path, exist_ok=True)
                popup.dismiss()
                self.refresh_folders()

        btn.bind(on_release=create)
        popup.open()


class FolderScreen(Screen):
    folder_name = ""

    def on_enter(self):
        self.refresh_photos()

    def folder_path(self):
        return os.path.join(App.get_running_app().vault_root, self.folder_name)

    def refresh_photos(self):
        grid = self.ids.photo_grid
        grid.clear_widgets()
        for fname in sorted(os.listdir(self.folder_path())):
            if fname.endswith(".enc"):
                grid.add_widget(Button(text=fname.replace(".enc", ""), size_hint_y=None, height=150))

    def add_photo(self):
        pick_image(self.on_photo_picked)

    def on_photo_picked(self, src_path):
        if not src_path:
            return
        fname = os.path.basename(src_path) + ".enc"
        dst_path = os.path.join(self.folder_path(), fname)
        crypto_utils.encrypt_file(src_path, dst_path)
        Clock.schedule_once(lambda dt: self.refresh_photos(), 0)


class VaultApp(App):
    def build(self):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ])
            private_dir = self.user_data_dir
        else:
            private_dir = os.path.join(os.getcwd(), "vault_private")
            os.makedirs(private_dir, exist_ok=True)

        self.vault_root = os.path.join(private_dir, VAULT_ROOT_NAME)
        os.makedirs(self.vault_root, exist_ok=True)
        crypto_utils.init(private_dir)

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LockScreen(name="lock"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(FolderScreen(name="folder"))
        sm.current = "lock"
        return sm


if __name__ == "__main__":
    VaultApp().run()
