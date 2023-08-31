<template>
  <div class="leadership-code">
    <!-- <header>
      <img class="blue-filter" src="@/assets/images/logo.png" height="36px" alt="" />
    </header> -->

    <div class="leadership-card">
      <h2>Enter Access code</h2>
      <div class="input__container">
        <input placeholder="Enter Code" autofocus v-model="code" type="text" />
      </div>
      <button :disabled="!code" type="submit" @click="handleApplyCode">Apply Code</button>
    </div>

    <div></div>
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
      } else {
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
  display: flex;
  flex-flow: column;
  align-items: flex-start;
  justify-content: center;
  color: $dark-black-blue;
  background-color: $offer-white;
  border-radius: 4px;
  gap: 16px;
  padding: 64px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family;
}

.leadership-code {
  padding: 0 32px 32px 32px;
  height: 100vh;
  font-family: $base-font-family;
  font-weight: 400;
  color: $dark-black-blue;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
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
  width: 320px;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  padding: 8px;
  border-radius: 4px;
  line-height: 1.75;
  border: 1px solid rgba(0, 0, 0, 0.1);
  outline: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family;
  font-weight: 400;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  margin-right: 1rem;
  resize: none;

  &:focus {
    outline: none;
  }

  &::placeholder {
    color: $very-light-gray;
  }
}

button {
  @include dark-blue-button();
  text-align: center;
  margin-bottom: 6px;
  width: 320px;
  padding: 12px;
  box-shadow: none;

  &:disabled {
    background-color: $off-white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    opacity: 0.7;
  }
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

h2 {
  font-family: $thin-font-family;
}

.blue-filter {
  filter: brightness(0) invert(48%) sepia(33%) saturate(348%) hue-rotate(161deg) brightness(91%)
    contrast(90%);
}
.header {
  display: flex;
  flex-direction: row;
  align-items: center;
  small {
    margin-right: 16px;
  }
}
header {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  font-family: $thin-font-family;
  font-size: 16px;
  padding-top: 12px;
}
</style>