<template>
  <div class="logZoomPage" :style="noRenderHeader ? 'margin-top: 0rem;' : ''">
    <div v-if="!noRenderHeader" class="alerts-header">
      <button @click="$router.push({ name: 'ListTemplates' })" class="back-button">
        <img class="invert" src="@/assets/images/left.svg" alt="" height="12px" />
        Back
      </button>

      <h3>Meeting Recaps</h3>

      <button
        class="green__button"
        v-if="!create"
        :disabled="!((channelCreated || recapChannel) && userIds.length > 0)"
        @click="handleRecapUpdate(recapChannel)"
      >
        Activate Channel
      </button>

      <button
        v-else
        class="green__button"
        @click="handleRecapUpdate(createdZoomChannel)"
        :disabled="!((channelCreated || recapChannel) && userIds.length > 0)"
      >
        Activate Channel
      </button>
    </div>

    <div v-else class="alerts-header-inner">
      <button @click="closeBuilder" class="back-button">
        <img src="@/assets/images/left.svg" height="14px" alt="" />
        Back
      </button>

      <h3>Meeting Recaps</h3>

      <button
        class="green__button"
        v-if="!create"
        :disabled="!((channelCreated || recapChannel) && userIds.length > 0)"
        @click="handleRecapUpdate(recapChannel)"
      >
        Activate Channel
      </button>

      <button
        v-else
        class="green__button"
        @click="handleRecapUpdate(createdZoomChannel)"
        :disabled="!((channelCreated || recapChannel) && userIds.length > 0)"
      >
        Activate Channel
      </button>
    </div>

    <div class="centered">
      <div class="section">
        <h4>Select Users</h4>
        <div>
          <Multiselect
            placeholder="Select Users"
            v-model="userIds"
            :options="userList"
            openDirection="below"
            style="width: 20vw"
            selectLabel="Enter"
            track-by="id"
            :custom-label="selectUsersCustomLabel"
            :multiple="true"
            :closeOnSelect="false"
          >
            <template slot="noResult">
              <p>No results.</p>
            </template>
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.svg" alt="" />
                Select Users
              </p>
            </template>
          </Multiselect>
        </div>
      </div>

      <div class="section">
        <h4>Select or create a Slack channel</h4>
        <div style="margin-bottom: 0.5rem" v-if="!channelName" class="row">
          <label :class="!create ? 'green' : ''">Select #channel</label>
          <ToggleCheckBox
            style="margin: 0.25rem"
            @input="changeCreate"
            :value="create"
            offColor="#41b883"
            onColor="#41b883"
          />
          <label :class="create ? 'green' : ''">Create #channel</label>
        </div>

        <label v-else for="channel" style="font-weight: bold"
          >Alerts will send to
          <span>{{ channelName }}</span>
        </label>
        <div v-if="create">
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
              class="green__button"
            >
              Create Channel
            </button>
          </div>
        </div>

        <div v-else>
          <FormField>
            <template v-slot:input>
              <Multiselect
                placeholder="Select Channel"
                v-model="recapChannel"
                :options="userChannelOpts.channels"
                openDirection="below"
                style="width: 20vw"
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

      <div></div>
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
  name: 'ZoomRecap',
  components: {
    ToggleCheckBox,
    FormField,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    noRenderHeader: {
      type: Boolean
    },
    closeBuilder: {
      type: Function,
    },
  },
  data() {
    return {
      dropdownLoading: false,
      create: true,
      userChannelOpts: new SlackListResponse(),
      channelName: '',
      channelCreated: false,
      recapChannel: '',
      createdZoomChannel: '',
      userIds: [],
      users: CollectionManager.create({ ModelClass: User }),
      userList: [],
    }
  },
  async created() {
    if (this.user.slackRef) {
      await this.listUserChannels()
    }
    if (this.user.userLevel == 'MANAGER') {
      await this.users.refresh()
      this.userList = this.users.list
    }
  },
  methods: {
    async handleRecapUpdate(recap_channel) {
      if (typeof recap_channel === 'object') {
        recap_channel = recap_channel.id
      }
      this.userIds = this.userIds.map((user) => user.id)
      const res = await SlackOAuth.api.updateRecapChannel(this.slackId, recap_channel, this.userIds)

      this.createdZoomChannel = ''
      this.recapChannel = ''
      this.$router.push({ name: 'ListTemplates' })
      // location.reload()
      this.$toast('Recap channel saved!', {
        timeout: 2000,
        position: 'top-left',
        type: 'success',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
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
    selectUsersCustomLabel(prop) {
      return prop.fullName.trim() ? prop.fullName : prop.email
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

.back-button {
  color: $base-gray;
  background-color: transparent;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
  font-size: 16px;
  letter-spacing: 0.75px;

  img {
    margin-right: 8px;
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
}
::placeholder {
  color: $very-light-gray;
  font-size: 0.75rem;
}
input[type='text']:focus {
  outline: none;
}
.logZoomPage {
  height: 100vh;
  color: $base-gray;
  margin-top: 5rem;
}
.section {
  background-color: white;
  box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  border: 1px solid $soft-gray;
  color: $base-gray;
  border-radius: 6px;
  width: 50vw;
  min-height: 25vh;
  letter-spacing: 0.75px;
  padding: 0px 0px 32px 12px;
  margin-top: 16px;
  &__head {
    padding: 8px 12px;
    background-color: white;
    margin-bottom: 0;
    // color: $very-light-gray;
  }
  &__body {
    padding: 6px 12px;
    background-color: white;
    font-size: 11px;
    color: $light-gray-blue;
    p {
      margin-top: 0;
    }
  }
}
.centered {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-weight: bold;
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
.alerts-header {
  position: fixed;
  z-index: 10;
  top: 0;
  left: 60px;
  background-color: $white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding: 8px 32px 0px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
    color: $light-gray-blue;
  }
}
.green__button {
  @include primary-button();
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 6px;
}
.green {
  color: #41b883;
}
input {
  border: 1px solid #e8e8e8;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
}
img {
  filter: invert(60%);
}
.invert {
  filter: invert(30%);
}
.alerts-header-inner {
  // position: fixed;
  z-index: 10;
  // top: 0;
  // left: 60px;
  background-color: $white;
  // width: 96vw;
  position: sticky;
  top: 0;
  width: 100%;
  border-bottom: 1px solid $soft-gray;
  padding: 8px 32px 0px 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    color: $light-gray-blue;
  }
}
</style>