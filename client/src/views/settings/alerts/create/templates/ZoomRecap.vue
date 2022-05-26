<template>
  <div class="logZoomPage">
    <div
      style="display: flex; align-item: center; justify-content: space-between; margin: 0vw 19vw"
    >
      <div>
        <h3>Meeting Recaps</h3>
        <p style="margin-top: -0.5rem; font-size: 14px; color: #9b9b9b">
          Recieve meeting recaps from essential team members
        </p>
      </div>

      <button @click="$router.push({ name: 'CreateNew' })" class="back-button">
        <img src="@/assets/images/back.png" alt="" />
        Back to workflows
      </button>
    </div>

    <div style="flex-direction: column" class="centered">
      <div class="card">
        <div
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: -0.6rem;
          "
        >
          <p style="text-align: center; font-weight: bold">Select Users</p>
          <div>
            <Multiselect
              placeholder="Select Users"
              v-model="userIds"
              :options="userList"
              openDirection="below"
              style="width: 14vw"
              selectLabel="Enter"
              track-by="id"
              label="fullName"
              :multiple="true"
              :closeOnSelect="false"
            >
              <template slot="noResult">
                <p>No results.</p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.png" alt="" />
                  Select Users
                </p>
              </template>
            </Multiselect>
          </div>
        </div>

        <div>
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

            <div v-if="!channelCreated" v style="margin-top: 1.25rem">
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
                  v-model="recapChannel"
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
                      <img src="@/assets/images/plusOne.png" alt="" />
                    </p>
                  </template>
                  <template slot="placeholder">
                    <p class="slot-icon">
                      <img src="@/assets/images/search.png" alt="" />
                      Select Channel
                    </p>
                  </template>
                </Multiselect>
              </template>
            </FormField>
          </div>
        </div>
      </div>
      <div v-if="(channelCreated || recapChannel) && userIds.length > 0" style="margin-top: 2rem">
        <div v-if="!create">
          <button class="green__button bouncy" @click="handleRecapUpdate(recapChannel)">
            Activate Channel
          </button>
        </div>
        <div v-else>
          <button class="green__button bouncy" @click="handleRecapUpdate(createdZoomChannel)">
            Activate Channel
          </button>
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
  name: 'ZoomRecap',
  components: {
    ToggleCheckBox,
    FormField,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      dropdownLoading: false,
      create: true,
      userChannelOpts: new SlackListResponse(),
      channelName: '',
      newChannel: {},
      channelCreated: false,
      slackAccount: {},
      recapChannel: '',
      recapChannelId: '',
      createdZoomChannel: '',
      userIds: [],
      pipelines: [],
      users: CollectionManager.create({ ModelClass: User }),
      userList: [],
      slack_id: [],
      alertTargetOpts: [
        { key: 'Myself', value: 'SELF' },
        { key: 'All Managers', value: 'MANAGERS' },
        { key: 'All Reps', value: 'REPS' },
        { key: 'Everyone', value: 'ALL' },
        { key: 'SDR', value: 'SDR' },
      ],
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
      this.$router.push({ name: 'CreateNew' })
      // location.reload()
      this.$Alert.alert({
        type: 'success',
        message: 'Workflow saved successfully',
        timeout: 2000,
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
    async createChannel(name) {
      const res = await SlackOAuth.api.createChannel(name)
      if (res.channel) {
        this.createdZoomChannel = res.channel.id
        this.channelCreated = !this.channelCreated
      } else {
        console.log(res.error)
        this.channelName = ''
        if (res.error == 'name_taken') {
          this.$Alert.alert({
            message: 'Channel name already taken',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name_maxlength') {
          this.$Alert.alert({
            message: 'Channel name exceeds maximum length',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'restricted_action') {
          this.$Alert.alert({
            message: 'A team preference is preventing you from creating channels',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name_specials') {
          this.$Alert.alert({
            message:
              'The only special characters allowed are hyphens and underscores. Channel names must also begin with a letter ',
            type: 'error',
            timeout: 3000,
          })
        } else if (res.error == 'org_login_required') {
          this.$Alert.alert({
            message:
              'The workspace is undergoing an enterprise migration and will not be available until migration is complete.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'ekm_access_denied') {
          this.$Alert.alert({
            message: 'Administrators have suspended the ability to post a message.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'too_many_convos_for_team') {
          this.$Alert.alert({
            message: 'The workspace has exceeded its limit of public and private channels.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'no_permission') {
          this.$Alert.alert({
            message:
              'The workspace token used in this request does not have the permissions necessary to complete the request. Make sure your app is a member of the conversation its attempting to post a message to.',
            type: 'error',
            timeout: 4000,
          })
        } else if (res.error == 'team_access_not_granted') {
          this.$Alert.alert({
            message:
              'You are not granted the specific workspace access required to complete this request.',
            type: 'error',
            timeout: 2000,
          })
        } else if (res.error == 'invalid_name') {
          this.$Alert.alert({
            message: 'Channel name invalid. Please try again',
            type: 'error',
            timeout: 2000,
          })
        } else {
          this.$Alert.alert({
            message: 'Something went wrong..Please try again',
            type: 'error',
            timeout: 2000,
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
.bouncy {
  animation: bounce 0.2s infinite alternate;
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
.card {
  display: flex;
  justify-content: space-evenly;
  align-items: flex-start;
  width: 60vw;
  padding: 3rem;
  background-color: $white;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  color: $base-gray;
}
.centered {
  margin-top: 1rem;
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
.green {
  color: #41b883;
}
.disabled__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $soft-gray;
  color: $gray;
  cursor: not-allowed;
  font-size: 14px;
}
input {
  border: 1px solid #e8e8e8;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
}
img {
  filter: invert(60%);
}
</style>