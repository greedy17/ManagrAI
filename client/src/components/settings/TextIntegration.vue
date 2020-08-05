<template>
  <div class="container">
    <div class="box">
      <div class="box__header">
        <div class="box__title">Message Integration</div>
      </div>
      <div class="box__content">
        <div class="status">
          <span>{{
            user.textConnected
              ? 'Your Account is Set up with the number' + user.messageAuthAccountRef.phoneNumber
              : 'You have not set up a messaging number please fill out the form below'
          }}</span>
        </div>
        <div v-if="!user.textConnected" class="message-setup">
          <div class="form-group">
            <label>State</label>
            <DropDownList
              v-if="!user.textConnected"
              :items="statesList"
              displayKey="name"
              valueKey="abbreviation"
              v-model="selectedState"
              @selected="onSelectedState"
            />
          </div>
          <div class="form-group">
            <label>Number</label>
            <div
              class="muted"
              v-if="!user.textConnected && showNumbersList && availablePhoneNumbers.length < 1"
            >
              No Results
            </div>
            <DropDownList
              v-if="
                !user.textConnected &&
                  showNumbersList &&
                  !loading &&
                  availablePhoneNumbers.length > 0
              "
              :items="availablePhoneNumbers"
              v-model="selected"
              displayKey="phoneNumber"
              valueKey="phoneNumber"
            />
          </div>
          <div class="selected-phone-details">
            <div class="details" v-if="fullSelectedNumberDetails">
              <div :key="details.phoneNumber" v-for="details in fullSelectedNumberDetails">
                <div class="form-group">
                  <span class="muted">Phone Number:</span>
                  {{ details.phoneNumber }}
                </div>
                <div class="form-group">
                  <span class="muted">Locality:</span>
                  {{ details.locality }}
                </div>
                <div class="form-group">
                  <span class="muted">Zip Code:</span>
                  {{ details.postalCode }}
                </div>
                <div class="form-group">
                  <span class="muted">Region:</span>
                  {{ details.region }}
                </div>
              </div>
            </div>
            <div v-else class="details">
              <span class="muted"> Please Select A number to see its details</span>
            </div>
          </div>
        </div>
        <div class="footer" v-if="!user.textConnected && this.selected">
          <button class="primary-button" @click="onSaveAccount">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import Messaging, { STATES } from '@/services/messages'
import DropDownSelect from '@/components/forms/DropDownSelect'
import User from '@/services/users'
import DropDownList from '@/components/shared/DropDownList'

export default {
  name: 'TextIntegration',
  components: { DropDownSelect, DropDownList },
  data() {
    return {
      filterBy: '',
      loading: false,
      emailsLoaded: false,
      threads: [],
      availablePhoneNumbers: [],
      selected: null,
      statesList: STATES,
      selectedState: null,
      showNumbersList: false,
    }
  },

  async created() {},
  methods: {
    ...mapActions(['refreshCurrentUser']),
    async onSelectedState(val) {
      this.loading = true
      this.showNumbersList = false
      this.availablePhoneNumbers = []
      this.availablePhoneNumbers = await Messaging.listAvailablePhoneNumbers(val)
      this.loading = false
      this.showNumbersList = true
    },
    async onSaveAccount() {
      this.loading = true
      try {
        await User.api.createMessagingAccount(this.selected)
      } finally {
        await this.refreshCurrentUser()
        this.loading = false
      }
    },
  },
  computed: {
    ...mapState(['user']),
    fullSelectedNumberDetails() {
      if (this.availablePhoneNumbers.length > 0) {
        return this.availablePhoneNumbers.filter(n => {
          return n.phoneNumber == this.selected
        })
      }
      return null
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';
@import '@/styles/forms';
@import '@/styles/variables';
@import '@/styles/containers';
@import '@/styles/layout';
.container {
  background-color: white;
}
.message-setup {
  display: flex;
  flex-direction: column;
}
.disconnect {
  @include button-danger;
}

.v-centered {
  align-items: center;
}

.form-group {
  display: flex;
  align-items: center;
  > * {
    margin: 1rem;
  }
}
</style>
