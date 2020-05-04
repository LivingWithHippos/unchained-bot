from debrid.constants import open_source_client_id


class CredentialsInterface:
    def save_credentials(self,
                         client_secret: str,
                         device_code: str,
                         refresh_token: str,
                         ci: str = open_source_client_id) -> bool:
        """save the credentials"""
        pass

    def update_refresh_token(self, refresh_token: str) -> bool:
        """Extract text from the currently loaded file."""
        pass
