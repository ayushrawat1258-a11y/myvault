"""
Bridges into native Android APIs from Python using pyjnius.
This ONLY works when running as a compiled Android APK (not on desktop).
"""
from kivy.utils import platform


def authenticate_fingerprint(on_success, on_error):
    if platform != "android":
        on_error("Fingerprint only works on a real Android device build.")
        return

    from jnius import autoclass, PythonJavaClass, java_method
    from android.runnable import run_on_ui_thread

    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    BiometricPrompt = autoclass('androidx.biometric.BiometricPrompt')
    PromptInfoBuilder = autoclass('androidx.biometric.BiometricPrompt$PromptInfo$Builder')
    ContextCompat = autoclass('androidx.core.content.ContextCompat')

    activity = PythonActivity.mActivity

    class AuthCallback(PythonJavaClass):
        __javainterfaces__ = ['androidx/biometric/BiometricPrompt$AuthenticationCallback']
        __javacontext__ = 'app'

        @java_method('(Landroidx/biometric/BiometricPrompt$AuthenticationResult;)V')
        def onAuthenticationSucceeded(self, result):
            on_success()

        @java_method('(ILjava/lang/CharSequence;)V')
        def onAuthenticationError(self, errorCode, errString):
            on_error(str(errString))

        @java_method('()V')
        def onAuthenticationFailed(self):
            on_error("Not recognized. Try again.")

    executor = ContextCompat.getMainExecutor(activity)
    callback = AuthCallback()
    prompt = BiometricPrompt(activity, executor, callback)

    info = (PromptInfoBuilder()
            .setTitle("Unlock Vault")
            .setSubtitle("Touch the fingerprint sensor")
            .setNegativeButtonText("Cancel")
            .build())

    @run_on_ui_thread
    def show():
        prompt.authenticate(info)

    show()


def pick_image(on_picked):
    if platform != "android":
        on_picked(None)
        return

    from android import activity
    from jnius import autoclass

    Intent = autoclass('android.content.Intent')
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    REQUEST_CODE = 1001

    def on_activity_result(request_code, result_code, intent):
        if request_code == REQUEST_CODE and intent:
            uri = intent.getData()
            path = _resolve_uri_to_path(uri)
            on_picked(path)
        else:
            on_picked(None)
        activity.unbind(on_activity_result=on_activity_result)

    activity.bind(on_activity_result=on_activity_result)

    intent = Intent(Intent.ACTION_PICK)
    intent.setType("image/*")
    PythonActivity.mActivity.startActivityForResult(intent, REQUEST_CODE)


def _resolve_uri_to_path(uri):
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    MediaColumns = autoclass('android.provider.MediaStore$Images$Media')
    activity = PythonActivity.mActivity
    cursor = activity.getContentResolver().query(uri, None, None, None, None)
    cursor.moveToFirst()
    idx = cursor.getColumnIndex(MediaColumns.DATA)
    path = cursor.getString(idx)
    cursor.close()
    return path
