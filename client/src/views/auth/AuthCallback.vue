<template>
  <div>
    <p>Loading...</p>
  </div>
</template>

<script>
import { PublicClientApplication, InteractionType } from '@azure/msal-browser';

export default {
  name: 'AuthCallback',
  mounted() {
    const config = {
      auth: {
        clientId: 'ead3f8ef-4a75-4620-b660-5d9c0999f8bc',
        authority: 'https://login.microsoftonline.com/common',
        redirectUri: 'http://localhost:8080/auth/callback',
      },
      cache: {
        cacheLocation: 'localStorage',
      },
    };

    const myMSALObj = new PublicClientApplication(config);

    myMSALObj.handleRedirectPromise().then(response => {
      if (response !== null) {
        console.log('response.accessToken', response.accessToken); // Access token for further API calls
      } else {
        console.log('Error during redirect callback.');
      }
    });
  },
};
</script>
