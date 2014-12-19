__author__ = 'wack'



from wx.py.shell import Shell

class RPShell(Shell):
    '''
    Wrapper for Shell to allow callback on command execution
    '''
    # allow to register a push callback function, which will be called after shell code was executed
    def registerPushCallBack(self, pushcallback=None):
        self.pushcallback = pushcallback

    # add callback to push function to facilitate interaction with gui
    def push(self, command, silent=False):
        super(RPShell, self).push(command, silent)
        # call callback if it was registered and command is complete and not empty
        if hasattr(self, "pushcallback") and not self.more and command.strip() != '':
            self.pushcallback( command)