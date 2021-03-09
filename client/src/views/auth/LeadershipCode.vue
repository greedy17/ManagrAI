<template>
  <div class="leadership-code">
    <img class="leadership-code__logo" src="@/assets/images/logo.png" />
    <h2>Welcome</h2>
    <div class="leadership-code__text">
      Please enter your Leadership code provided by the managr team.
    </div>
    <div class="input__container">
      Enter Code <input v-model="code" type="text" class="leadership-code__input" />
    </div>
    <button type="submit" @click="handleApplyCode">Apply Code</button>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'LeadershipCode',
  components: {},
  data() {
    const LEADERSHIP_CODE = 'M@n@gr!100'
    return {
      code: '',
      leadershipCode: LEADERSHIP_CODE,
    }
  },
  methods: {
    handleApplyCode() {
      if (this.code === this.leadershipCode) {
        this.$router.push({ name: 'Register' })
      } else {
        this.$Alert.alert({
          type: 'error',
          message: 'Invalid Leadership Code, please try again.',
          duration: '4500',
        })
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

.leadership-code {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background-color: white;

  &__logo {
    height: 5rem;
  }

  &__text {
    color: #{$mid-gray};
    font-family: #{$base-font-family};
    width: 100%;
    max-width: 20rem;
    margin-bottom: 4rem;
  }

  &__input {
    @include input-field-white();
    width: 19rem;
    // height: 1rem !important;
    // border: 2px solid red;
  }
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  color: $main-font-gray;
  text-align: center;
  font-size: 20px;
  margin-bottom: 2rem;
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
  margin-top: 1.25rem;
  height: 2.25rem;
  border-radius: 3px;
  width: 19rem;
}

.hidden {
  display: none;
}
</style>
