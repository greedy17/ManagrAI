<template>
  <div class="logZoomPage">
    <div class="zoom-header">
      <div>
        <h3>Log Meetings</h3>
        <p style="margin-top: -0.5rem; font-size: 14px; color: #9b9b9b">
          Log meetings and save attendees right after the meeting ends
        </p>
      </div>

      <button @click="$router.push({ name: 'CreateNew' })" class="back-button">
        <img class="invert" src="@/assets/images/back.svg" alt="" />
        Back to workflows
      </button>
    </div>

    <div style="margin-top: -2rem" class="flex-start">
      <div class="card centered">
        <div>
          <div v-if="!channelName" class="row">
            <label :class="!create ? 'green' : ''">Select channel</label>
            <ToggleCheckBox
              style="margin: 0.25rem"
              @input="changeCreate"
              :value="create"
              offColor="#41b883"
              onColor="#41b883"
            />
            <label :class="create ? 'green' : ''">Create channel</label>
          </div>

          <label v-else for="channel" style="font-weight: bold"
            >Alerts will send to
            <span style="color: #41b883; font-size: 1.2rem">{{ channelName }}</span>
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
                v-if="channelName"
                @click="createChannel(channelName)"
                class="green__button bouncy"
              >
                Create Channel
              </button>
              <button v-else class="disabled__button">Create Channel</button>
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
                  style="min-width: 13vw"
                  selectLabel="Enter"
                  track-by="id"
                  label="name"
                  :loading="dropdownLoading"
                >
                  <template slot="noResult">
                    <p class="multi-slot">No results. Try loading more</p>
                  </template>
                  <template slot="afterList">
                    <p
                      class="multi-slot__more"
                      @click="listUserChannels(userChannelOpts.nextCursor)"
                    >
                      Load More
                      <img src="@/assets/images/plusOne.svg" class="invert" alt="" />
                    </p>
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
          <div style="margin-top: 1.5rem" v-if="channelCreated || zoomChannel">
            <div v-if="!create">
              <button class="green__button bouncy" @click="handleZoomUpdate(zoomChannel)">
                Activate Channel
              </button>
            </div>
            <div v-else>
              <button class="green__button bouncy" @click="handleZoomUpdate(createdZoomChannel)">
                Activate Channel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import FormField from '@/components/forms/FormField'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import { CollectionManager } from '@thinknimble/tn-models'
import User from '@/services/users'

export default {
  name: 'LogZoom',
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
      newChannel: {},
      channelCreated: false,
      slackAccount: {},
      zoomChannel: '',
      createdZoomChannel: '',
      users: CollectionManager.create({ ModelClass: User }),
    }
  },
  async created() {
    if (this.user.slackRef) {
      await this.listUserChannels()
    }
    if (this.user.userLevel == 'MANAGER') {
      await this.users.refresh()
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
            this.$store.commit('UPDATE_USER', response)
          })
        })
      } finally {
        this.$router.push({ name: 'CreateNew' })
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
      return this.$store.state.user
    },
    slackId() {
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
.bouncy {
  animation: bounce 0.2s infinite alternate;
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
.back-button {
  font-size: 14px;
  color: $dark-green;
  background-color: transparent;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
  margin: 1rem 0rem 0rem 0rem;

  img {
    height: 1rem;
    margin-right: 0.5rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
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
}
img {
  filter: invert(70%);
}
.invert {
  filter: invert(80%);
}
.green {
  color: #41b883;
  font-weight: 400;
}
::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
}
.logZoomPage {
  height: 100vh;
  color: $base-gray;
  margin-top: 4rem;
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
.green__button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.5rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: $white;
  background-color: $dark-green;
  cursor: pointer;
  height: 2rem;
  font-weight: bold;
  font-size: 1.02rem;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  color: $gray;
  cursor: not-allowed;
  font-size: 16px;
}
input {
  box-shadow: 3px 4px 7px $very-light-gray;
  border: 1px solid white;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
}
</style>