<template>
  <div class="logZoomPage">
    <div>
      <h2 style="font-weight: bold; text-align: center">
        <span style="color: black">
          Log
          <span style="color: #5f8cff">Zoom Meeting Recaps</span>
        </span>
      </h2>
      <p style="text-align: center; color: black; font-weight: bold">
        Recieve zoom meeting recaps from essential team members
      </p>
    </div>

    <div style="margin-top: -2rem" class="centered">
      <!-- <div class="card">
        <div :key="value" v-for="(key, value) in userTargetsOpts">
          <label for="key">{{ key.fullName }}</label>
          <input id="key" type="radio" />
        </div>
      </div> -->

      <div class="card">
        <div>
          <select name="reipients" id="recipients">
            <option :key="value" v-for="(key, value) in userTargetsOpts" :value="value">
              {{ key.fullName }}
            </option>
          </select>
        </div>

        <div>
          <div v-if="!channelName" class="row">
            <label>Select #channel</label>
            <ToggleCheckBox
              style="margin: 0.25rem"
              @input="changeCreate"
              :value="create"
              offColor="#199e54"
              onColor="#199e54"
            />
            <label>Create #channel</label>
          </div>

          <label v-else for="channel" style="font-weight: bold"
            >Alerts will send to
            <span style="color: #199e54; font-size: 1.2rem">{{ channelName }}</span>
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
              @input="logNewName(channelName)"
            />

            <div v-if="!channelCreated" v style="margin-top: 1.25rem">
              <button v-if="channelName" @click="createChannel(channelName)" class="green__button">
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
                <DropDownSearch
                  :items.sync="userChannelOpts.channels"
                  v-model="zoomChannel"
                  displayKey="name"
                  valueKey="id"
                  nullDisplay="Channels"
                  :hasNext="!!userChannelOpts.nextCursor"
                  @load-more="listChannels(userChannelOpts.nextCursor)"
                  searchable
                  local
                >
                  <template v-slot:tn-dropdown-option="{ option }">
                    <img
                      v-if="option.isPrivate == true"
                      class="card-img"
                      style="width: 1.2rem; height: 1rem; margin-right: 0.2rem"
                      src="@/assets/images/lock.png"
                    />
                    {{ option['name'] }}
                  </template>
                </DropDownSearch>
              </template>
            </FormField>

            <p
              v-if="zoomChannel"
              @click="removeZoomChannel"
              :class="zoomChannel ? 'selected__item' : 'visible'"
            >
              <img
                src="@/assets/images/remove.png"
                style="height: 1rem; margin-right: 0.25rem; margin-top: 0.25rem"
                alt=""
              />
              {{ getChannelName(zoomChannel) }}
            </p>
          </div>
        </div>
      </div>
      <!-- <div style="margin-top: 2rem">
        <div>
          <button class="green__button">prev</button>
        </div>
        <div>
          <button class="green__button">Next</button>
        </div>
      </div> -->
    </div>
  </div>
</template>

<script>
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import FormField from '@/components/forms/FormField'
import DropDownSearch from '@/components/DropDownSearch'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import User from '@/services/users'

export default {
  name: 'ZoomRecap',
  components: {
    DropDownSearch,
    ToggleCheckBox,
    FormField,
  },
  data() {
    return {
      create: true,
      userChannelOpts: new SlackListResponse(),
      channelName: '',
      newChannel: {},
      channelCreated: false,
      slackAccount: {},
      zoomChannel: '',
      createdZoomChannel: '',
      users: CollectionManager.create({ ModelClass: User }),
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
    }
  },
  methods: {
    async handleZoomUpdate(zoom_channel) {
      const res = await SlackOAuth.api.updateZoomChannel(this.slackId, zoom_channel)
      this.createdZoomChannel = ''
      this.zoomChannel = ''
      this.$router.push({ name: 'CreateNew' })
      this.$Alert.alert({
        type: 'success',
        message: 'Alert saved successfully',
        timeout: 2000,
      })
    },
    removeZoomChannel() {
      this.zoomChannel = ''
    },
    logNewName(str) {
      let new_str = ''
      new_str = str.replace(/\s+/g, '-').toLowerCase()
      this.channelName = new_str
    },
    changeCreate() {
      this.create = !this.create
    },
    getChannelName(id) {
      return this.userChannelOpts.channels.filter((channel) => channel.id == id)[0].name
    },
    async listUserChannels(cursor = null) {
      const res = await SlackOAuth.api.listUserChannels(cursor)
      const results = new SlackListResponse({
        channels: [...this.userChannelOpts.channels, ...res.channels],
        responseMetadata: { nextCursor: res.nextCursor },
      })
      this.userChannelOpts = results
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
    userTargetsOpts() {
      if (this.user.userLevel == 'MANAGER') {
        return [
          ...this.alertTargetOpts.map((opt) => {
            return {
              id: opt.value,
              fullName: opt.key,
            }
          }),
          ...this.users.list,
        ]
      } else {
        return [{ fullName: 'Myself', id: 'SELF' }]
      }
    },
    async onSearchUsers(v) {
      this.users.pagination = new Pagination()
      this.users.filters = {
        ...this.users.filters,
        search: v,
      }
      await this.users.refresh()
    },
    async onUsersNextPage() {
      await this.users.addNextPage()
    },
  },
  //   mounted() {
  //     console.log(this.user)
  //     console.log(this.$store.state.user.slackRef.slackId)
  //   },
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

.logZoomPage {
  height: 100vh;
  color: white;
  margin-top: 4rem;
}
.card {
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  width: 60vw;
  height: 225px;
  background-color: $panther;
  border-radius: 0.5rem;
}
.centered {
  margin-top: 4rem;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60vh;
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
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $panther-silver;
  color: $panther-gray;
  cursor: not-allowed;
  height: 2rem;
  width: 10rem;
  font-weight: bold;
  font-size: 1.02rem;
}
input {
  -webkit-box-shadow: 1px 4px 7px black;
  box-shadow: 1px 4px 7px black;
  border: 1px solid white;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
}
.selected__item {
  padding: 0.5rem 1.5rem;
  border: 2px solid white;
  border-radius: 0.3rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -0.25rem;
}
.visible {
  display: none;
}
</style>