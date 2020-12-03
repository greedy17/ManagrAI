<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">TRIGGER PASSWORD UPDATE/RESET</div>
      </div>
      <div class="box__content">
        <div class="form">
          <div class="form__element">
            <button class="button" @click.prevent="onGetEmail" v-if="!loading">
              Get Email
            </button>
            <ComponentLoadingSVG style="margin: unset" v-else />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'Password',
  data() {
    return {
      loading: false,
    }
  },
  methods: {
    onGetEmail() {
      // NOTE (Bruno 6-18-2020) once we get password-reset-flow incorporated, we can use User.api herein and complete this page.
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
</style>
