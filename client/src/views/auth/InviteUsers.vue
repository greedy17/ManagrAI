<template>
  <div class="invite-users">
    <div class="invite-users__header">
      <h3 style="color: #4d4e4c">Manage Your Team</h3>

      <button class="invite_button" type="submit" @click="handleInvite">
        Invite Member
        <img
          v-if="hasSlack"
          style="height: 0.8rem; margin-left: 0.25rem"
          src="@/assets/images/slackLogo.png"
          alt=""
        />
        <img
          v-else
          style="height: 0.8rem; margin-left: 0.25rem"
          src="@/assets/images/logo.png"
          alt=""
        />
      </button>
    </div>

    <Invite class="invite-users__inviter" :inviteOpen="inviteOpen" @cancel="handleCancel" />

    <section>
      <header class="invite-users__header">
        <h3 style="color: #4d4e4c">Update your Info</h3>

        <button class="invite_button" type="submit" @click="handleUpdate">
          Update
          <img style="height: 0.8rem; margin-left: 0.25rem" src="@/assets/images/logo.png" alt="" />
        </button>
      </header>

      <form class="update-container">
        <input
          v-model="profileForm.field.firstName.value"
          placeholder="First Name"
          :errors="profileForm.field.firstName.errors"
          id="user-input"
        />
        <input
          v-model="profileForm.field.lastName.value"
          placeholder="Last Name"
          :errors="profileForm.field.lastName.errors"
          id="user-input"
        />

        <Multiselect
          placeholder="Select Timezone"
          style="width: 16rem"
          v-model="selectedTimezone"
          @input="setTime"
          :options="timezones"
          openDirection="below"
          selectLabel="Enter"
          label="key"
          track-by="value"
        />
      </form>
    </section>

    <section>
      <header class="invite-users__header">
        <h3 style="color: #4d4e4c">Note Templates</h3>

        <button
          :disabled="!noteSubject || !noteBody"
          class="invite_button"
          type="submit"
          @click="createTemplate"
          v-if="!savingTemplate"
        >
          Save Template
          <!-- <img style="height: 0.8rem; margin-left: 0.25rem" src="@/assets/images/logo.png" alt="" /> -->
        </button>

        <div v-else>
          <PipelineLoader />
        </div>
      </header>

      <div class="update-container">
        <input
          v-model="noteSubject"
          class="template-input"
          type="text"
          name=""
          id=""
          :disabled="savingTemplate"
          placeholder="Template Title"
        />

        <quill-editor
          :disabled="savingTemplate"
          ref="message-body"
          :options="{
            modules: {
              toolbar: { container: ['bold'] },
            },
            placeholder: 'Type out your template here.',
          }"
          v-model="noteBody"
          class="message__box"
        />
      </div>
    </section>
  </div>
</template>

<script>
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'
import PipelineLoader from '@/components/PipelineLoader'
import Invite from '../settings/_pages/_Invite'
import User from '@/services/users'
import { UserProfileForm } from '@/services/users/forms'
import { quillEditor } from 'vue-quill-editor'
import moment from 'moment-timezone'

export default {
  name: 'InviteUsers',
  components: {
    Invite,
    quillEditor,
    PipelineLoader,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      savingTemplate: false,
      noteSubject: null,
      noteBody: null,
      inviteOpen: false,
      selectedTimezone: null,
      user: this.getUser,
      timezones: moment.tz.names(),
      profileForm: new UserProfileForm({}),
      loading: false,
    }
  },
  methods: {
    async createTemplate() {
      this.savingTemplate = true
      try {
        const res = await User.api.createTemplate({
          subject: this.noteSubject,
          body: this.noteBody,
          user: this.getUser.id,
        })
        this.$toast('Note template created successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log(e)
        this.$toast('Error creating template', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.savingTemplate = false
        this.noteSubject = null
        this.noteBody = null
      }
    },
    setTime() {
      this.profileForm.field.timezone.value = this.selectedTimezone.value
    },
    handleInvite() {
      this.inviteOpen = !this.inviteOpen
    },
    handleCancel() {
      this.inviteOpen = false
    },
    handleUpdate() {
      this.loading = true
      User.api
        .update(this.getUser.id, this.profileForm.value)
        .then((response) => {
          this.$toast('Sucessfully updated profile info', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
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
  computed: {
    getUser() {
      return this.$store.state.user
    },
    isAdmin() {
      return this.$store.state.user.isAdmin
    },
    hasSlack() {
      return !!this.$store.state.user.slackRef
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

::v-deep .ql-toolbar.ql-snow {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  border-top-left-radius: 4px;
  border-top-right-radius: 4px;
}
::v-deep .ql-container.ql-snow {
  border-bottom-left-radius: 4px;
  border-bottom-right-radius: 4px;
}
.message__box {
  margin-bottom: 2rem;
  height: 24vh;
  width: 32vw;
  border-radius: 0.25rem;
  background-color: transparent;
}
.template-input {
  border: 1px solid #ccc;
  border-radius: 0.3rem;
  padding-left: 1rem;
  height: 50px;
  width: 32vw;
  font-family: inherit;
  margin-bottom: 1rem;
}
.template-input:focus {
  outline: none;
}
.update-container {
  background-color: $white;
  border: 1px solid #e8e8e8;
  color: $base-gray;
  width: 60vw;
  height: 40vh;
  overflow: scroll;
  padding: 1.5rem 0rem 1.5rem 1rem;
  border-radius: 5px;
  display: flex;
  align-items: flex-start;
  flex-direction: column;
}
#user-input {
  border: 1px solid #e8e8e8;
  border-radius: 0.3rem;
  background-color: white;
  min-height: 2.5rem;
  width: 16rem;
  margin-bottom: 1rem;
  font-family: $base-font-family;
}
#user-input:focus {
  outline: none;
}
.invite-users {
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  margin-top: 4rem;
  &__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 60vw;
    padding: 0.25rem;
  }

  &__inviter {
    margin-top: 2rem;
  }
}

h2 {
  @include base-font-styles();
  font-weight: bold;
  text-align: center;
  font-size: 20px;
  margin-bottom: 2rem;
}

.invite_button {
  color: $dark-green;
  background-color: white;
  border-radius: 0.25rem;
  transition: all 0.25s;
  padding: 0.5rem 0.75rem;
  font-weight: bolder;
  font-size: 14px;
  border: 1px solid #e8e8e8;
}
.invite_button:disabled {
  color: $base-gray;
  background-color: $soft-gray;
  border-radius: 0.25rem;
  transition: all 0.25s;
  padding: 0.5rem 0.75rem;
  font-weight: 400px;
  font-size: 14px;
  border: 1px solid #e8e8e8;
}

.invite_button:hover {
  cursor: pointer;
  transform: scale(1.025);
  box-shadow: 1px 2px 3px $mid-gray;
}
</style>
