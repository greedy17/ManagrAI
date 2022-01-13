<template>
  <div class="profile-page">
    <div class="profile-page__form">
      <img class="back-logo" src="@/assets/images/logo.png" />
      <FormField
        v-model="profileForm.field.firstName.value"
        placeholder="First Name"
        :errors="profileForm.field.firstName.errors"
        name="first-name"
        id="first-name"
        label="First Name"
      ></FormField>
      <FormField
        v-model="profileForm.field.lastName.value"
        placeholder="Last Name"
        :errors="profileForm.field.lastName.errors"
        name="last-name"
        id="last-name"
        label="Last Name"
      ></FormField>
      <FormField :errors="profileForm.field.timezone.errors" label="Timezone">
        <template v-slot:input>
          <DropDownSearch
            :items.sync="timezones"
            v-model="profileForm.field.timezone.value"
            nullDisplay="Select your timezone"
            searchable
            local
            @input="profileForm.field.timezone.validate()"
          />
        </template>
      </FormField>

      <div style="width: 100%; display: flex; justify-content: flex-end; flex-direction: row">
        <PulseLoadingSpinnerButton
          @click="handleUpdate"
          class="update-button"
          text="Update"
          :loading="loading"
          >Update</PulseLoadingSpinnerButton
        >
      </div>
    </div>
  </div>
</template>

<script>
import User from '@/services/users'
import { UserProfileForm } from '@/services/users/forms'
import DropDownSearch from '@/components/DropDownSearch'
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

import FormField from '@/components/forms/FormField'

import moment from 'moment-timezone'

export default {
  name: 'ProfilePage',
  components: { FormField, DropDownSearch, PulseLoadingSpinnerButton },
  data() {
    return {
      user: this.getUser,
      timezones: moment.tz.names(),
      profileForm: new UserProfileForm({}),
      loading: false,
    }
  },
  async created() {
    this.profileForm = new UserProfileForm({
      firstName: this.getUser.firstName,
      lastName: this.getUser.lastName,
      timezone: this.getUser.timezone,
    })
    this.timezones = this.timezones.map((tz) => {
      return { key: tz, value: tz }
    })
  },
  methods: {
    handleUpdate() {
      this.loading = true
      User.api
        .update(this.getUser.id, this.profileForm.value)
        .then((response) => {
          this.$Alert.alert({
            message: 'Successfully Updated Profile info',
            type: 'success',
            timeout: 2000,
          })
          this.$store.dispatch('updateUser', User.fromAPI(response.data))

          this.resetProfileForm()
        })
        .catch((e) => {
          console.log(e)
          this.resetProfileForm()
        })
    },
    resetProfileForm() {
      this.profileForm.firstName = this.getUser.firstName
      this.profileForm.lastName = this.getUser.lastName
      this.profileForm.timezone = this.getUser.timezone
      this.loading = false
    },
  },
  computed: {
    getUser() {
      return this.$store.state.user
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.dropdown {
  ::v-deep .selected-items[data-v-515df75a] {
    max-height: 40px;
  }
}
.profile-page {
  margin-top: 4rem;
  padding: 2rem 2rem;
  @media only screen and (max-width: 768px) {
    /* For mobile phones: */
    padding: 0rem;
  }
}
::v-deep .input-content {
  box-shadow: 0px 2px 3px $very-light-gray;
  border: none;
}
::v-deep .tn-dropdown__selection-container {
  background: transparent;
  border: none;
}
::v-deep .tn-input {
  width: 100%;
  display: flex;
  justify-content: center;
}
.profile-page__form {
  @include standard-border();
  position: relative;
  left: 35%;
  padding: 1rem 2rem;
  margin-top: 3.125rem;
  width: 31.25rem;
  min-height: 15rem;
  height: auto;
  background-color: $white;
  box-shadow: 3px 4px 7px $very-light-gray;
  border: none;
  border-radius: 0.5rem;
  color: $base-gray;
  display: flex;
  flex-flow: column;
  align-items: center;
  @media only screen and (max-width: 768px) {
    /* For mobile phones: */
    width: 100%;
    height: 100%;
    padding: 0rem;
    left: 0;
    display: block;
    border: 0;
  }
}

.update-button {
  background-color: $dark-green;
  color: white;
  margin-top: 1.25rem;
  height: 2.5rem;
  width: 6rem;
  font-size: 14px;
}
button {
  @include primary-button();
  margin-top: 1.25rem;
  height: 2.5rem;
  width: 19rem;
  font-size: 14px;
}
.back-logo {
  position: absolute;
  opacity: 0.06;
  filter: alpha(opacity=50);
  height: 90%;
  margin-top: -1.5rem;
  margin-left: -2rem;
}
</style>
