<template>
  <div class="logZoomPage">
    <div
      style="position: sticky; z-index: 2; top: 0; background-color: white; font-size: 16px"
      class="zoom-header"
    >
      <div>
        <p style="font-size: 16px; letter-spacing: 0.75px">
          Log meetings and save attendees right after the meeting ends
        </p>
      </div>
    </div>

    <div style="margin-top: -3rem" class="flex-start">
      <div class="card centered">
        <div>
          <div v-if="!channelName" class="row">
            <label :class="!create ? '' : 'gray'">Select channel</label>
            <ToggleCheckBox
              style="margin: 0.25rem"
              @input="changeCreate"
              :value="create"
              offColor="#41b883"
              onColor="#41b883"
            />
            <label :class="create ? '' : 'gray'">Create channel</label>
          </div>

          <label v-else for="channel" style="font-weight: bold"
            >Meetings will send to
            <span>{{ channelName }}</span>
            channel</label
          >
          <div
            style="
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: flex-start;
            "
            v-if="create"
          >
            <input
              v-model="channelName"
              class="search__input"
              type="text"
              name="channel"
              id="channel"
              placeholder="Name your channel"
              @input="logNewName(channelName)"
            />

            <div v-if="!channelCreated" style="margin-top: 1.25rem">
              <button
                :disabled="!channelName"
                @click="createChannel(channelName)"
                class="primary-button"
              >
                Create Channel
              </button>
            </div>
          </div>

          <div
            style="
              display: flex;
              flex-direction: column;
              align-items: center;
              justify-content: flex-start;
            "
            v-else
          >
            <FormField>
              <template v-slot:input>
                <Multiselect
                  placeholder="Select Channel"
                  v-model="zoomChannel"
                  :options="userChannelOpts.channels"
                  openDirection="below"
                  selectLabel="Enter"
                  track-by="id"
                  label="name"
                  style="width: 30vw"
                  :loading="dropdownLoading"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results. Try loading more</p>
                  </template>
                  <template slot="afterList">
                    <p
                      v-if="userChannelOpts.nextCursor"
                      class="multi-slot__more"
                      @click="listUserChannels(userChannelOpts.nextCursor)"
                    >
                      Load More
                      <img src="@/assets/images/plusOne.svg" alt="" />
                    </p>
                    <p v-else></p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.svg" alt="" />
                      Select Channel
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
        </div>
      </div>
    </div>

    <div class="bottom-right">
      <div v-if="!create">
        <button
          class="primary-button"
          :disabled="!(channelCreated || zoomChannel)"
          @click="handleZoomUpdate(zoomChannel)"
        >
          Activate Channel
        </button>
      </div>
      <div v-else>
        <button
          class="primary-button"
          :disabled="!(channelCreated || zoomChannel)"
          @click="handleZoomUpdate(createdZoomChannel)"
        >
          Activate Channel
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import FormField from '@/components/forms/FormField'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import User from '@/services/users'
import { decryptData, encryptData } from '../../encryption'

export default {
  name: 'OnboardingLogMeeting',
  components: {
    ToggleCheckBox,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    FormField,
  },
  data() {
    return {
      dropdownLoading: true,
      create: true,
      userChannelOpts: new SlackListResponse(),
      channelName: '',
      channelCreated: false,
      zoomChannel: '',
      createdZoomChannel: '',
    }
  },
  async created() {
    if (this.user.slackRef) {
      await this.listUserChannels()
    }
  },
  methods: {
    async handleZoomUpdate(zoom_channel) {
      if (typeof zoom_channel === 'object') {
        zoom_channel = zoom_channel.id
      }
      try {
        const res = await SlackOAuth.api.updateZoomChannel(this.slackId, zoom_channel).then(() => {
          User.api.getUser(this.user.id).then((response) => {
            // const encrypted = encryptData(response, process.env.VUE_APP_SECRET_KEY)
            // this.$store.commit('UPDATE_USER', encrypted)
            this.$store.commit('UPDATE_USER', response)
          })
        })
      } finally {
        this.$emit('close-form-modal')
        this.$router.push({ name: 'ListTemplates' })
        this.$toast('Workflow saved successfully', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    logNewName(str) {
      let new_str = ''
      new_str = str.replace(/\s+/g, '-').toLowerCase()
      this.channelName = new_str
    },
    changeCreate() {
      this.create = !this.create
    },
    async listUserChannels(cursor = null) {
      this.dropdownLoading = true
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
      setTimeout(() => {
        this.dropdownLoading = false
      }, 500)
    },
    async createChannel(name) {
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.createdZoomChannel = res.channel.id
        this.channelCreated = !this.channelCreated
      } else {
        console.log(res.error)
        this.channelName = ''
        if (res.error == 'name_taken') {
          this.$toast('Channel name already taken', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'invalid_name_maxlength') {
          this.$toast('Channel name exceeds max-length', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'restricted_action') {
          this.$toast('A team preference is preventing you from creating channels', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'invalid_name_specials') {
          this.$toast(
            'The only special characters allowed are hyphens and underscores. Channel names must also begin with a letter ',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'org_login_required') {
          this.$toast(
            'The workspace is undergoing an enterprise migration and will not be available until migration is complete.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'too_many_convos_for_team') {
          this.$toast('The workspace has exceeded its limit of public and private channels.', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else if (res.error == 'no_permission') {
          this.$toast(
            'The workspace token used in this request does not have the permissions necessary to complete the request. Make sure your app is a member of the conversation its attempting to post a message to.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'team_access_not_granted') {
          this.$toast(
            'You are not granted the specific workspace access required to complete this request.',
            {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            },
          )
        } else if (res.error == 'invalid_name') {
          this.$toast('Channel name invalid. Please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Something went wrong, please try again', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          console.log(res.error)
        }
      }
    },
  },
  computed: {
    user() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user
    },
    slackId() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return this.$store.state.user.slackRef.slackId
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.primary-button {
  box-shadow: none;
  font-size: 13px;
}
.primary-button:disabled {
  background-color: $soft-gray;
}
.primary-button:hover {
  background-color: $soft-gray !important;
  cursor: text;
}
.flex-start {
  display: flex;
  align-items: flex-start;
  justify-content: center;
  flex-direction: column;
}
.zoom-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
  width: 700px;
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.search__input {
  min-height: 40px;
  display: block;
  padding: 8px 40px 8px 8px;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
  background: #fff;
  font-size: 14px;
  box-shadow: none;
  width: 30vw;
}
img {
  filter: invert(70%);
}
.gray {
  color: $light-gray-blue;
}
::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
}
.logZoomPage {
  height: 100vh;
  color: $base-gray;
  margin: 2rem 1rem;
  display: flex;
  align-items: center;
  flex-direction: column;
}
.card {
  width: 700px;
  height: 250px;
  background-color: $white;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
}
input[type='text']:focus {
  outline: none;
}
.centered {
  margin-top: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-weight: bold;
}
input {
  box-shadow: 3px 4px 7px $very-light-gray;
  border: 1px solid white;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
}
.bottom-right {
  position: absolute;
  bottom: 0;
  right: 0;
  margin: 0 1rem 1rem 0;
}
</style>