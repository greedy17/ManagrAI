<template>
  <div id="google-signin-button"></div>
</template>
  
<script>
import { GoogleAuth } from 'google-signin-client'
  
export default {
  mounted() {
    const auth = new GoogleAuth({
      client_id: '1053178983159-40pr5voodgitli9ap0v9uifj8d3p9mgq.apps.googleusercontent.com',
      scope: 'email profile'
    })

    auth.install().then(() => {
      const signInButton = document.getElementById('google-signin-button')
      auth.render(signInButton)
    })
  }
}
</script>
  