<template>
  <div class="leadership-code">
    <!-- <header>
      <img class="blue-filter" src="@/assets/images/logo.png" height="36px" alt="" />
    </header> -->

    <div v-if="!sentEmail" class="leadership-card">
      <h2 class="h2-text" style="margin-bottom: -0.5rem;">Sign up for Managr</h2>
      <p class="small-text">Fill in the information below to get started</p>
      <div class="input__container">
        <p class="input__container_label">Company Name:</p>
        <input id="access-code" autofocus v-model="orgName" type="text" />
      </div>
      <div class="input__container">
        <p class="input__container_label">Full Name:</p>
        <input id="access-code" v-model="name" type="text" />
      </div>
      <div class="input__container">
        <p class="input__container_label">Email (company email only):</p>
        <input id="access-code" v-model="email" type="text" />
      </div>
      <button id="access-code-button" class="submit-button" :disabled="!email || !name || !orgName" type="submit" @click="handleSendEmail">Email Registration Link</button>
    </div>

    <div v-else class="leadership-card">
      <h2>Registeration link sent!</h2>
      <div class="input__container">
        <p style="margin-top: 0;">Please check your email and spam folder</p>
      </div>
      <!-- <button @click="returnHome">Back</button> -->
      <button @click="resendEmail">Resend Email</button>
    </div>

    <div></div>
  </div>
</template>

<script>
import User from '@/services/users'

export default {
  name: 'LeadershipCode',
  data() {
    const LEADERSHIP_CODE = 'M@n@gr!200'
    return {
      email: '',
      name: '',
      orgName: '',
      userID: null,
      leadershipCode: LEADERSHIP_CODE,
      sentEmail: false,
    }
  },
  created() {
    // this.$router.push({ name: 'AdminRegistration', params: { validCode: true } })
  },
  methods: {
    returnHome() {
      this.$router.go()
    },
    async resendEmail() {
      try {
        await User.api.sendEmail({ user_id: this.userID })
        this.$toast('Email sent! Please check your inbox and spam.', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch(e) {
        console.log('error in resend email', e)
      }
    },
    async handleSendEmail() {
      if (!this.email || !this.name || !this.orgName) {
        return
      }

      if (!this.email.includes('@') || !this.email.includes('.')) {
        
      }
      if (!this.name.split(' ')[1]) {
        this.$toast('Please enter your full name', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      if (this.email.includes('@gmail.com')) {
        this.$toast('Please use a company email', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
        return
      }
      const nameSplit = this.name.split(' ')
      const firstName = nameSplit[0]
      const lastName = nameSplit.slice(1, nameSplit.length).join(' ')
      const data = {
        role: 'PR',
        first_name: firstName,
        last_name: lastName,
        email: this.email,
        organization_name: this.orgName,
        is_paid: false,
      }
      try {
        const invite = await User.api.adminInvite(data)
        console.log('invite', invite)
        // const invitedAdminLink = invite.data.activation_link_ref
        // const subject = 'Managr Free Account'
        // const body = `Hey ${firstName},\n\nYour account is ready!\n\nClick here to get started: [Managr Account](${invitedAdminLink})\n\nIf you have questions or need help email: customers@managr.ai`
        // await User.api.sendEmail({ subject, body, to: this.email })
        this.userID = invite.data.id
        await User.api.sendEmail({ user_id: invite.data.id })
        this.sentEmail = true
      } catch(e) {
        console.log('error in handleSendEmail', e)
        if (e.response && e.response.data) {
          const data = e.response.data
          console.log('data', data)
          for (let key in data) {
            this.$toast(data[key][0], {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          }
        } else {
          this.$toast('Error sending email', {
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
.h2-text {
  font-size: 1.4rem;
  color: $dark-black-blue;
}
.small-text {
  font-size: 12px;
  margin-top: 0;
  margin-bottom: 1rem;
  color: $base-gray;
}
.input__container {
  display: flex;
  flex-direction: column;
}
.input__container_label {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 13px;
}
.submit-button {
  font-family: $thin-font-family;
}
</style>