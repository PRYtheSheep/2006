class User():
    """
    Defines the base user class which will be inherited by the landlord, tenant and admin classes
    """
    def __init__(self, username: str, email: str, password :str):
        """
        :param username: username of the user
        :param email: email of the user
        :param password: password of the user
        """
        self.username = username
        self.email = email
        self.password = password

    def getUsername(self) -> str:
        """
        :return: user username
        """
        return self.username

    def setUsername(self, newUsername: str):
        """
        :param newusername: new user username
        :return: None
        """
        self.username = newUsername

    def getEmail(self) -> str:
        """
        :return: user email
        """
        return self.email

    def setEmail(self, newEmail: str):
        """
        :param newEmail: new user email
        :return: None
        """
        self.email = newEmail

    def getPassword(self) -> str:
        """
        :return: user password
        """
        return self.password

    def setPassword(self, newPassword: str):
        """
        :param newPassword: new user password
        :return: None
        """
        self.password = newPassword