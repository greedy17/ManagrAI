<template>
  <div class="registration">
    <div class="registration-card">
      <div class="registration__form">
        <div class="form-card">
          <h2>Register</h2>

          <span>
            <label for="name">Full Name</label>
            <input
              @blur="registrationForm.field.fullName.validate()"
              :errors="registrationForm.field.fullName.errors"
              v-model="registrationForm.field.fullName.value"
              placeholder=""
              id="name"
            />
          </span>

          <span>
            <label for="email">Email</label>
            <input
              @blur="registrationForm.field.email.validate()"
              :errors="registrationForm.field.email.errors"
              v-model="registrationForm.field.email.value"
              type="email"
              id="email"
            />
          </span>

          <span>
            <label for="password">Set a Password</label>
            <input
              id="password"
              @blur="showVals(registrationForm.field.password)"
              :errors="registrationForm.field.password.errors"
              v-model="registrationForm.field.password.value"
              type="password"
            />
          </span>

          <span>
            <label for="confirm-password">Re-Enter Password</label>
            <input
              id="confirm-password"
              label="Re-Enter Password"
              @blur="registrationForm.field.confirmPassword.validate()"
              :errors="registrationForm.field.confirmPassword.errors"
              v-model="registrationForm.field.confirmPassword.value"
              type="password"
            />
          </span>

          <span>
            <label for="company">Company</label>
            <input
              @blur="registrationForm.field.organizationName.validate()"
              :errors="registrationForm.field.organizationName.errors"
              v-model="registrationForm.field.organizationName.value"
              placeholder=""
              id="company"
            />
          </span>

          <Multiselect
            placeholder="Select User Role"
            @input="tester($event)"
            v-model="userRole"
            :options="userRoles"
            openDirection="above"
            style="width: 45vw; margin-top: 4px"
            selectLabel="Enter"
            label="name"
          >
            <template slot="noResult">
              <p>No results.</p>
            </template>
          </Multiselect>

          <!-- <div>
            <span class="gray">{{ userTime }}</span>
            <p v-if="!changeZone" @click="selectZone" class="time">Change timezone ?</p>
            <p v-else @click="selectZone" class="time">Select your timezone:</p>
          </div> -->

          <FormField>
            <template v-slot:input>
              <Multiselect
                :placeholder="userTime"
                @input="test($event)"
                v-model="selectedZone"
                :options="timezones"
                openDirection="above"
                style="width: 45vw; margin-top: 4px"
                selectLabel="Enter"
                label="key"
              >
                <template slot="noResult">
                  <p>No results.</p>
                </template>
              </Multiselect>
            </template>
          </FormField>

          <div class="form-card__footer">
            <div>
              By clicking Sign Up, I agree to the
              <a href="https://managr.ai/terms-of-service" target="_blank">Terms of Service</a> and
              <a href="https://managr.ai/privacy-policy" target="_blank">Privacy Policy</a>.
            </div>

            <Button class="registration__button" type="submit" @click="onSubmit" text="Sign Up" />
          </div>
        </div>

        <!-- <div style="margin-top: 1rem">
          <router-link :to="{ name: 'Login' }">Back to Login</router-link>
        </div> -->
      </div>
    </div>
  </div>
</template>

<script>
import User, { UserRegistrationForm } from '@/services/users'

import Button from '@thinknimble/button'
import FormField from '@/components/forms/FormField'
import moment from 'moment-timezone'

export default {
  name: 'Registration',
  components: {
    FormField,
    Button,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      User,
      submitting: false,
      registrationForm: new UserRegistrationForm(),
      userRoles: User.roleChoices,
      timezones: moment.tz.names(),
      userTime: moment.tz.guess(),
      changeZone: false,
      userRole: null,
      selectedZone: null,
    }
  },
  created() {
    const validCode = this.$route.params.validCode

    if (!validCode) {
      // redirects to enter code registration screen if they try to get there without putting in leaderrshop code
      this.$router.push({
        name: 'Register',
      })
    }
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })
  },
  methods: {
    showVals(val) {
      let errors = []
      // errors =
    },
    selectZone() {
      this.changeZone = !this.changeZone
    },
    test(n) {
      this.registrationForm.field.timezone.value = n.value
    },
    tester(n) {
      this.registrationForm.field.role.value = n.key
    },
    async onSubmit() {
      this.registrationForm.validate()

      // Do not continue if the form has errors
      if (!this.registrationForm.isValid) {
        this.$toast('Please complete all fields.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      // Continue with user registration...
      this.submitting = true

      let user
      try {
        user = await User.api.register(this.registrationForm)
      } catch (error) {
        this.$toast('There was a problem creating your account.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        throw error
      } finally {
        this.submitting = false
      }

      // Update the user in the store to "log in" and navigate to integrations
      this.$store.commit('UPDATE_USER', user)
      this.$store.commit('UPDATE_USERTOKEN', user.token)
      this.$router.push({ name: 'ListTemplates' })
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  mounted() {
    this.registrationForm.field.timezone.value = this.userTime
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

::v-deep .tn-input__label {
  color: $light-gray-blue;
}

.registration {
  display: flex;
  padding: 2rem 0rem 0rem 0rem;
  flex-flow: column;
  justify-content: center;
  // max-width: 24rem;
  // margin: 1.5rem auto;

  &__text {
    color: $base-gray;
    font-family: #{$base-font-family};
    margin-bottom: 1rem;
    text-align: center;
    font-size: 14px;
  }
  &__privacy {
    padding: 0.5rem 1rem;
    font-size: 0.75rem;
    margin-top: 0.5rem;
    letter-spacing: 0.75px;
  }

  &__button {
    @include primary-button();
    width: 10rem;
    border-radius: 6px;
    margin-top: 1rem;
    box-shadow: none;
  }
}

.header {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  margin-left: 44vw;

  img {
    height: 1.5rem;
    margin-right: 0.25rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}

.time {
  color: $base-gray;
  cursor: pointer;
  font-size: 14px;
}
::v-deep .multiselect__placeholder {
  color: $light-gray-blue;
}
.time:hover {
  color: $gray;
}
.form-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-evenly;
  flex-direction: column;
  gap: 12px;
  border-radius: 6px;
  background-color: white;
  // border: 1px solid #e8e8e8;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  padding: 1rem 2rem;
  width: 50vw;
  color: $base-gray;
  letter-spacing: 0.75px;

  &__footer {
    font-size: 12px;
  }
}
a {
  text-decoration: none;
}
.registration__form {
  background-color: transparent !important;
  display: flex;
  flex-flow: column;
  align-items: center;
}

// input {
//   height: 2.5rem;
//   width: 100%;
//   display: block;
//   margin: 1rem;

//   &:disabled {
//     border: 2px solid $dark-green;
//   }
// }

input {
  width: 45vw;
  border-radius: 4px;
  padding: 10px;
  border: 1px solid $soft-gray;
}
input:focus {
  outline: none;
}

label {
  font-size: 13px;
  color: $light-gray-blue;
}

// button {
//   @include primary-button();
//   margin-top: 1.25rem;
//   height: 1.875rem;
//   width: 9.375rem;
// }
a {
  color: $dark-green;
  font-weight: bold;
}
</style>