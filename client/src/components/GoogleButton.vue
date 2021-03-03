<template>
  <div class="google-btn">
    <img class="google-btn__img" src="@/assets/images/google-btn/btn_google_light_normal_ios.svg" />
    SIGN IN WITH GOOGLE
  </div>
</template>

<script>
export default {
  name: 'GoogleButton',
}
</script>

<style lang="scss" scoped>
// These styles based on Google's branding guidelines
// https://developers.google.com/identity/branding-guidelines
.google-btn {
  width: 100%;
  padding: 0 0.5rem;
  padding-right: 1.5rem;
  display: flex;
  font-family: 'Roboto Medium', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  color: rgba(0, 0, 0, 0.54);

  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.35);
  align-items: center;

  cursor: pointer;

  &__img {
  }
}
</style>
