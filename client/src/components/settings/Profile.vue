<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">UPDATE PROFILE INFORMATION</div>
      </div>
      <div class="box__content">
        <div class="form">
          <div class="form__element">
            <div class="form__element-header">First Name:</div>
            <input type="text" class="form__input" v-model="first" />
            <div
              class="form__element-error"
              v-if="isFormValid !== null && !isFormValid && errors.firstNameIsBlank"
            >
              Must not be blank.
            </div>
          </div>
          <div class="form__element">
            <div class="form__element-header">Last Name:</div>
            <input type="text" class="form__input" v-model="last" />
            <div
              class="form__element-error"
              v-if="isFormValid !== null && !isFormValid && errors.lastNameIsBlank"
            >
              Must not be blank.
            </div>
          </div>
          <div class="form__element">
            <button class="button" @click.prevent="onUpdate" v-if="!loading">Update</button>
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
  name: 'Profile',
  components: {},
  data() {
    return {
      first: '',
      last: '',
      isFormValid: null,
      errors: {},
      loading: false,
    }
  },
  methods: {
    onUpdate() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.errors = {}

      // check form data for this request
      let [isFormValid, errors] = this.clientSideValidations()
      this.isFormValid = isFormValid
      this.errors = errors
      if (!this.isFormValid) {
        return
      }

      this.loading = true
      let patchData = {
        firstName: this.first,
        lastName: this.last,
      }
      User.api
        .update(this.$store.state.user.id, patchData)
        .then(response => {
          this.$store.dispatch('updateUser', User.fromAPI(response.data))
          this.first = ''
          this.last = ''
          this.$Alert.alert({
            type: 'success',
            timeout: 4000,
            message: 'Profile updated.',
          })
        })
        .finally(() => {
          this.loading = false
        })
    },
    clientSideValidations() {
      let formErrors = {
        firstNameIsBlank: this.firstNameIsBlank,
        lastNameIsBlank: this.lastNameIsBlank,
      }
      let isFormValid = !this.firstNameIsBlank && !this.lastNameIsBlank

      return [isFormValid, formErrors]
    },
  },
  computed: {
    firstNameIsBlank() {
      return !this.first.trim().length
    },
    lastNameIsBlank() {
      return !this.last.trim().length
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/mixins/inputs';
@import '@/styles/forms';
</style>
