<template>
  <div @click="$emit('click')" :class="{ 'google-btn': !loading }">
    <template v-if="!loading">
      <img
        class="google-btn__img"
        src="@/assets/images/google-btn/btn_google_light_normal_ios.svg"
      />
      SIGN IN WITH GOOGLE
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
