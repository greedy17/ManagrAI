<template>
  <div @click="$emit('click')" :class="{ 'google-btn': !loading }">
    <template v-if="!loading">
      <img
        class="google-btn__img"
        src="@/assets/images/google-btn/btn_google_light_normal_ios.svg"
      />
      Sign in
    </template>
    <template v-else>
      <PulseLoadingSpinnerButton :loading="loading"></PulseLoadingSpinnerButton>
    </template>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
export default {
  name: 'GoogleButton',
  props: {
    loading: {
      type: Boolean,
      default: false,
    },
  },
  components: {
    PulseLoadingSpinnerButton,
  },
}
</script>

<style lang="scss" scoped>
// These styles based on Google's branding guidelines
// https://developers.google.com/identity/branding-guidelines
.google-btn {
  width: 100%;
  padding: 0 0.25rem;
  padding-right: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'Roboto Medium', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  color: black;
  background-color: white;
  border-radius: 0.25rem;
  box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.35);
  cursor: pointer;

  &__img {
  }
}
</style>
