<template>
  <div class="leadership-code">
    <div class="leadership-card">
      <img class="leadership-code__logo" src="@/assets/images/logo.png" />
      <!-- <div class="seperator">
        <span>Welcome</span>
      </div> -->
      <h2 class="leadership-code__text">Please enter your Leadership code</h2>
      <div class="input__container">
        <input placeholder="Enter Code" v-model="code" type="text" class="leadership-code__input" />
      </div>
      <button :disabled="!code" type="submit" @click="handleApplyCode">Apply Code</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LeadershipCode',
  data() {
    const LEADERSHIP_CODE = 'M@n@gr!200'
    return {
      code: '',
      leadershipCode: LEADERSHIP_CODE,
    }
  },
  methods: {
    handleApplyCode() {
      if (Object.keys(this.$store.state.googleSignIn).length) {
        this.$router.push({ name: 'GoogleRegister', params: { validCode: true } })
      }
      else {
        if (this.code === this.leadershipCode) {
          this.$router.push({ name: 'AdminRegistration', params: { validCode: true } })
        } else {
          this.$toast('Invalid Leadership code. please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.leadership-card {
  margin-top: 2rem;
  background-color: white;
  // border: 1px solid #e8e8e8;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  border-radius: 0.5rem;
  padding: 3rem;
  color: $base-gray;
}

.leadership-code {
  height: 86vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background-color: transparent;
  letter-spacing: 0.75px;
  &__logo {
    height: 4rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(87%) contrast(89%);
  }

  &__text {
    color: $base-gray;
    font-family: #{$base-font-family};
    width: 100%;
    margin: 2rem 0rem;
    letter-spacing: 0.8px;
  }

  &__input {
    @include input-field-white();
    outline: none;
    width: 22vw;
  }

  &__input:focus,
  &__input:active {
    outline: none !important;
    box-shadow: none;
  }
}

input:focus {
  outline: none !important;
}

h2 {
  @include base-font-styles();
  text-align: center;
  font-size: 18px;
  margin-bottom: 1rem;
}

form {
  @include standard-border();
  margin-top: 3.125rem;
  width: 31.25rem;
  height: 18.75rem;
  background-color: $white;
  display: flex;
  flex-flow: column;
  align-items: center;
}

input {
  @include input-field();
  height: 2.5rem;
  width: 19rem;
  display: block;
  margin: 0.625rem 0;
  padding: 0 0 0 1rem;

  &:disabled {
    border: 2px solid $dark-green;
  }

  &:focus {
    outline: none;
  }
}

.input {
  &__container {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
  }
}

button {
  @include primary-button();
  margin-top: 1rem;
  border-radius: 6px;
  width: 22vw;
  padding: 12px;
  font-size: 15px;
  box-shadow: none;
}

.seperator {
  border-bottom: 1px solid $soft-gray;
  width: 100%;
  position: relative;
  margin: 16px 0px;

  span {
    position: absolute;
    left: 46%;
    top: -8px;
    background-color: white;
    padding: 0 8px;
    color: $light-gray-blue;
    font-size: 13px;
  }
}
</style>