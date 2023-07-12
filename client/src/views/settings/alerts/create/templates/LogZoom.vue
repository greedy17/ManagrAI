<template>
  <div class="logZoomPage" :style="noRenderHeader ? 'margin-top: 0rem;' : ''">
    <div v-if="!noRenderHeader" class="alerts-header">
      <button @click="$router.push({ name: 'ListTemplates' })" class="back-button">
        <img class="invert" src="@/assets/images/left.svg" alt="" height="12px" />
        Back
      </button>

      <h3>Log Meetings</h3>

      <button
        class="green__button"
        v-if="!create"
        :disabled="!(channelCreated || zoomChannel)"
        @click="handleZoomUpdate(zoomChannel)"
      >
        Activate Channel
      </button>

      <button
        v-else
        class="green__button"
        @click="handleZoomUpdate(createdZoomChannel)"
        :disabled="!(channelCreated || zoomChannel)"
      >
        Activate Channel
      </button>
    </div>

    <!-- <div v-else class="alerts-header-inner">
      <button @click="closeBuilder" class="back-button">
        <img src="@/assets/images/left.svg" height="14px" alt="" />
        Back
      </button>

      <h3>Log Meetings</h3>

      <button
        class="green__button"
        v-if="!create"
        :disabled="!(channelCreated || zoomChannel)"
        @click="handleZoomUpdate(zoomChannel)"
      >
        Activate Channel
      </button>

      <button
        v-else
        class="green__button"
        @click="handleZoomUpdate(createdZoomChannel)"
        :disabled="!(channelCreated || zoomChannel)"
      >
        Activate Channel
      </button>
    </div> -->

    <div class="">
      <h4 class="card-text">Select a channel for your meetings</h4>
      <div class="section" style="padding-top: 1rem;">
        <!-- <div v-if="!channelName" class="row">
          <label :class="!create ? 'green' : ''">Select channel</label>
          <ToggleCheckBox
            style="margin: 0.25rem"
            @input="changeCreate"
            :value="create"
            offColor="#41b883"
            onColor="#41b883"
          />
          <label :class="create ? 'green' : ''">Create channel</label>
        </div> -->
        
        <div class="switcher">
          <div @click="switchChannelView('SELECT')" :class="!create ? 'activeSwitch' : ''" class="switch-item">
            <!-- <img src="@/assets/images/crmlist.svg" height="16px" alt="" /> -->
            Select channel
          </div>
          <div
            @click="switchChannelView('CREATE')"
            :class="create ? 'activeSwitch' : ''"
            class="switch-item"
          >
            <!-- <img src="@/assets/images/note.svg" height="12px" alt="" /> -->
            Create channel
          </div>
          <!-- <div style="cursor: not-allowed" class="switch-item">
            <img src="@/assets/images/callsummary.svg" height="14px" alt="" />
            Summaries
          </div> -->
        </div>

        <!-- <label v-else for="channel" style="font-weight: bold"
          >Alerts will send to
          <span style="color: #41b883; font-size: 1.2rem">{{ channelName }}</span>
          channel</label
        > -->
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
              class="green__button"
            >
              Create Channel
            </button>
          </div>
        </div>

        <div style="margin-top: 0.5rem; display: flex; flex-direction: column; align-items: center;" v-else>
          <FormField>
            <template v-slot:input>
              <Multiselect
                placeholder="Select Channel"
                v-model="zoomChannel"
                :options="userChannelOpts.channels"
                openDirection="below"
                style="width: 20vw; margin-top: 8px"
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
      <div class="invite-form__actions">
        <!-- <div style="width: 10vw;"></div> -->
        <div class="confirm-cancel-container" style="width: 90%; margin-bottom: 0.6rem;">
          <div class="img-border-modal cancel-button" @click="closePopularModal" style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 1rem;">
            Cancel
          </div>
          <!-- <PulseLoadingSpinnerButton
            :loading="savingTemplate"
            :class="!verifySubmit() || savingTemplate ? 'disabled__button' : 'purple__button'"
            text="Save"
            @click.stop="onSave"
            :disabled="!verifySubmit() || savingTemplate"
          /> -->
          <button 
            class="img-border-modal save" 
            :disabled="!(channelCreated || zoomChannel)"
            @click="handleZoomUpdate(zoomChannel)" 
            style="font-size: 13px; margin-bottom: 0.5rem; margin-top: 1rem;"
          >
            Activate
          </button>
        </div>
        <!-- <div class="invite-form__inner_actions">
          <template>
            <PulseLoadingSpinnerButton
              @click="onRevoke(removeApp)"
              class="invite-button modal-button"
              style="width: 5rem; margin-right: 5%; height: 2rem"
              text="Confirm"
              :loading="pulseLoading"
              >Confirm</PulseLoadingSpinnerButton
            >
          </template>
        </div> -->
      </div>
    </div>
    <!-- <div style="margin-top: 1.5rem" v-if="channelCreated || zoomChannel">
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
          </div> -->
  </div>
</template>

<script>
import ToggleCheckBox from '@thinknimble/togglecheckbox'
import FormField from '@/components/forms/FormField'
import SlackOAuth, { SlackListResponse } from '@/services/slack'
import User from '@/services/users'
import { decryptData, encryptData } from '../../../../../encryption'

export default {
  name: 'LogZoom',
  components: {
    ToggleCheckBox,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    FormField,
  },
  props: {
    noRenderHeader: {
      type: Boolean
    },
    closeBuilder: {
      type: Function,
    },
    canSave: { 
      type: Function
    },
    saveWorkflow: { 
      type: Function 
    },
    closePopularModal: {
      type: Function
    },
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
        this.$router.push({ name: 'ListTemplates' })
        this.$toast('Zoom channel saved!', {
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
    switchChannelView(view) {
      if (view === 'SELECT') {
        this.create = false
      } else if (view === 'CREATE') {
        this.create = true
      }
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
@import '@/styles/modals';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
// .bouncy {
//   animation: bounce 0.2s infinite alternate;
// }
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
.section {
  background-color: $off-white;
  width: 33vw;
  // box-shadow: 1px 1px 2px 1px rgba($very-light-gray, 50%);
  // border: 1px solid $soft-gray;
  color: $base-gray;
  border-radius: 6px;
  // width: 50vw;
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
  filter: invert(30%);
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
  // height: 100vh;
  color: $base-gray;
  margin-top: 4rem;
  display: flex;
  align-items: center;
  flex-direction: column;
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
  @include primary-button();
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
}
input {
  box-shadow: 3px 4px 7px $very-light-gray;
  border: 1px solid white;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
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
.invite-form {
  // @include small-modal();
  // min-width: 37vw;
  // min-height: 64vh;
  // align-items: center;
  // justify-content: space-between;
  color: $base-gray;
  &__title {
    font-weight: bold;
    text-align: left;
    font-size: 22px;
  }
  &__subtitle {
    text-align: left;
    font-size: 16px;
    margin-left: 1rem;
  }
  &__actions {
    display: flex;
    // justify-content: flex-end;
    // width: 100%;
    width: 36.5vw;
    position: absolute;
    bottom: 35%;
    // margin-top: -4rem;
  }
  &__inner_actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    border-top: 1px solid $soft-gray;
  }
  &__actions-noslack {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 1rem;
  }
}
.confirm-cancel-container {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  width: 94%;
  border-top: 1px solid $soft-gray;
  background-color: $white;
}
.img-border-modal {
  // @include gray-text-button();
  display: flex;
  align-items: center;
  justify-content: center;
  // padding: 4px 6px;
  margin-right: 8px;
  margin-top: 0.5rem;
}
.cancel-button {
  @include gray-button();
}
.save {
  @include primary-button();
  padding: 8px 24px;
}
.card-text {
  font-size: 11px;
  color: $light-gray-blue;
  margin: 0.25rem 0 0 0.75rem;
}
.switcher {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  background-color: $off-white;
  border: 1px solid $off-white;
  border-radius: 6px;
  padding: 2px 0;
  width: 100%;
  margin-bottom: 0.5rem;
}
.switch-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 0.25rem;
  border-radius: 6px;
  width: 100%;
  margin: 0 2px;
  cursor: pointer;
  color: $light-gray-blue;
  white-space: nowrap;
  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-left: -0.25rem;
  }
}

.activeSwitch {
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $base-gray;
  img {
    filter: none;
  }
}
</style>