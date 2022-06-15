<template>
  <div class="staff">
    <Modal
      v-if="editOpModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetEdit()
        }
      "
    >
      <div v-if="modalInfo">
        <div>{{modalInfo}}</div>
      </div>
      <div v-else>No Modal Info</div>
    </Modal>
    <div class="staff__drawer">
      <h3>Quick Commands</h3>
      <div class="command_dropdown">
        <Multiselect
          placeholder="Select Command"
          style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
          v-model="selectedCommand"
          :options="commandOptions"
          openDirection="below"
          selectLabel="Enter"
          track-by="value"
          label="label"
        >
          <template slot="noResult">
            <p class="multi-slot">No results.</p>
          </template>
        </Multiselect>
        <button class="green_button sized" @click="runCommand">></button>
      </div>
      <!-- <div :key="i" v-for="(org, i) in organizations.list">
        <div>{{org}}</div>
        <h2 @click="selected_org = org.id">{{ org.name }}</h2>
      </div> -->
      <h3>Organizations</h3>
      <Multiselect
        placeholder="Select Organization"
        style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
        v-model="selected_org"
        :options="organizations.list"
        openDirection="below"
        selectLabel="Enter"
        track-by="value"
        label="name"
      >
        <template slot="noResult">
          <p class="multi-slot">No results.</p>
        </template>
      </Multiselect>
    </div>
    <div class="staff__main_page">
      <template v-if="selected_org && selected_org.id">
        <div v-if="loading">Loading</div>
        <template v-else>
          <div style="border-bottom: 1px solid black; margin-left: 1rem">
            <!-- top bar here  -->
            <!-- {{selected_org}} -->
            <div>
              <div>State</div>
              <Multiselect
                placeholder="State"
                style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                v-model="stateActive"
                :options="states"
                openDirection="below"
                selectLabel="Enter"
                track-by="id"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
              </Multiselect>
            </div>
            <div>
              <div>Ignore Emails</div>
              <input 
                class="wide" 
                type="search" 
                v-model="ignoreEmailText" 
                placeholder="Ignore Emails" 
                @keyup.enter="ignoreEmail"
              />
            </div>
            <div>
              <div @click="test">Has Products</div>
              <input 
                type="checkbox" 
                v-model="hasProducts" 
              />
            </div>
            <button class="green_button" @click="goToUser(selectedUsers)">Go</button>
          </div>
          

          <!-- <div>{{allForms}}</div> -->
          <div class="form__list">
            <div class="form__list_item">
              <h3>Users</h3>
              <Multiselect
                placeholder="Select Users"
                style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                v-model="selectedUsers"
                :options="orgUsers"
                openDirection="below"
                selectLabel="Enter"
                track-by="id"
                label="fullName"
                :multiple="true"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
              </Multiselect>
              <button class="green_button" @click="goToUser(selectedUsers)">Go</button>
            </div>
            <div class="form__list_item">
              <h3>Slack Form</h3>
              <Multiselect
                placeholder="Select Slack Form"
                style="max-width: 20vw; margin-bottom: 1rem; margin-top: 1rem"
                v-model="selectedSlackForms"
                :options="orgSlackForms"
                openDirection="below"
                selectLabel="Enter"
                track-by="id"
                :custom-label="slackFormLabel"
                :multiple="true"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
              </Multiselect>
              <button class="green_button" @click="goToSlackForm()">Go</button>
            </div>
            <div class="form__list_item">
              <h3>Slack Form Instances</h3>
            </div>
            <div class="form__list_item">
              <h3>Meeting Workflows</h3>
              <button class="green_button" @click="goToMeetingWorkflow()">Go</button>
            </div>
          </div>
          <hr />
          <div class="form__List">
            <div :key="i" class="field__list_item" v-for="(workflow, i) in orgMeetingWorkflows">
              <h4>
                {{ 'event_data' in workflow.meeting_ref ? 'Google Meet' : 'Zoom Meeting' }} --
                {{
                  'event_data' in workflow.meeting_ref
                    ? workflow.meeting_ref['event_data']['title']
                    : workflow.meeting_ref.topic
                }}
              </h4>
              <ul>
                <li
                  v-for="(participant, index) in workflow.meeting_ref.participants"
                  :key="participant['email']"
                >
                  {{ participant['email'] }}
                </li>
              </ul>
            </div>
          </div>
        </template>
      </template>
      <template v-else-if="page === 'Users'">
        <div v-for="(user, i) in selectedUsers" :key="user.id">
          <div>
            <button class="green_button back" @click="goBack">Back</button>
            <h2 class="user_title">User {{i + 1}}</h2>
          </div>
          <div class="user_item_container">
            <h3>First Name:</h3>
            <h4>{{user.firstName}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Last Name:</h3>
            <h4>{{user.lastName}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Email:</h3>
            <h4>{{user.email}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Active:</h3>
            <h4>{{user.isActive}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Invited:</h3>
            <h4>{{user.isInvited}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Admin:</h3>
            <h4>{{user.isAdmin}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Staff:</h3>
            <h4>{{user.isStaff}}</h4>
          </div>
          <div class="user_item_container">
            <h3>User Level:</h3>
            <h4>{{user.userLevel}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Role:</h3>
            <h4>{{user.role}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Timezone:</h3>
            <h4>{{user.timezone}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Reminders:</h3>
            <!-- <h4>{{user.isInvited}}</h4> -->
            <h4>???</h4>
          </div>
          <div class="user_item_container">
            <h3>Activated Managr Configs:</h3>
            <h4>{{user.activatedManagrConfigs}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Slack ID:</h3>
            <h4>{{user.slackRef.slackId}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Channel:</h3>
            <h4>{{user.slackAccount.channel}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Organization Slack:</h3>
            <!-- VV This is clearly wrong. Figure out where list of these are VV -->
            <h4>{{user.organizationRef.slackIntegration}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Revoked:</h3>
            <h4>???</h4>
          </div>
          <div class="user_item_container">
            <h3>Is Onboarded:</h3>
            <h4>{{user.onboarding}}</h4>
          </div>
          <div class="user_item_container">
            <h3>Zoom Channel:</h3>
            <div v-if="user.slackAccount.zoomChannel">
              <h4>{{user.slackAccount.zoomChannel}}</h4>
            </div>
            <div v-else>
              <h4>null</h4>
            </div>
          </div>
          <div class="user_item_container">
            <h3>Recap Channel:</h3>
            <div v-if="user.slackAccount.recapChannel">
              <h4>{{user.slackAccount.recapChannel}}</h4>
            </div>
            <div v-else>
              <h4>null</h4>
            </div>
          </div>
          <div class="user_item_container">
            <h3>Recap Recievers:</h3>
            <div v-if="user.slackAccount.recapReceivers.length">
              <div v-for="(receiver) in user.slackAccount.recapReceivers" :key="receiver">
                <h4>{{user.receiver}}</h4>
              </div>
            </div>
            <div v-else>null</div>
          </div>
          <div class="user_item_container">
            <h3>Recap Channel:</h3>
            <div v-if="user.slackAccount.realtimeAlertConfigs.length">
              <h4>{{user.slackAccountrealtimeAlertConfigs}}</h4>
            </div>
            <div v-else>
              <h4>null</h4>
            </div>
          </div>
          <div>
            <div class="user_item_container">
              <h3>Zoom ID:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Email:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Type:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Role Name:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Timezone:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Host Key:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Account ID:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Language:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Status:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Access Token:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Refresh Token:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Token Generated Date:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Token Scope:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Is Revoked:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Refresh Token Task:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Fake Meeting ID:</h3>
              <h4>???</h4>
            </div>
          </div>
          <div>
            <div class="user_item_container">
              <h3>Auth Account:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Salesloft ID:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Guid:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Is Active:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Email:</h3>
              <h4>???</h4>
            </div>
            <div class="user_item_container">
              <h3>Team ID:</h3>
              <h4>???</h4>
            </div>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'SlackForm'">
        <div v-for="(slackForm, i) in selectedSlackForms" :key="slackForm.id">
          <div>
            <button class="green_button back" @click="goBack">Back</button>
            <h2 class="user_title">Slack Form {{i + 1}}</h2>
          </div>
          <h4>{{slackForm}}</h4>
          <div v-for="(fieldRef) in slackForm.fieldsRef" :key="fieldRef.id">
            <h3>Label: {{fieldRef.label}}</h3>
            <h3>Order: {{fieldRef.order}}</h3>
          </div>
        </div>
      </template>
      <template v-else-if="page === 'MeetingWorkflow'">
        <!-- <div>{{orgMeetingWorkflows[0]}}</div> -->
        <button class="green_button back" @click="goBack">Back</button>
        <div v-for="(meetingWorkflow) in orgMeetingWorkflows" :key="meetingWorkflow.id">
          <h3 @click="openModal(meetingWorkflow)">{{meetingWorkflow.meeting_ref.topic}}</h3>
          <!-- <h3>Full Name: {{slackForm.fullName}}</h3> -->
          <!-- <h3>Email: {{slackForm.email}}</h3> -->
          <!-- <h3>Role: {{slackForm.role}}</h3> -->
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import SlackOAuth from '@/services/slack'
import { SObjects, SObjectPicklist, MeetingWorkflows } from '@/services/salesforce'
import CollectionManager from '@/services/collectionManager'
import Organization from '@/services/organizations'
import COMMANDS from './staff-constants'
import User from '@/services/users'

export default {
  name: 'Staff',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  data() {
    return {
      commandOptions: [
        { label: 'Salesforce Resources', value: 'SALESFORCE_RESOURCES' },
        { label: 'Salesforce Fields', value: 'SALESFORCE_FIELDS' },
      ],
      allUsers: CollectionManager.create({
        ModelClass: User,
      }),
      selectedUsers: null,
      selectedSlackForms: null,
      orgUsers: null,
      orgSlackForms: null,
      selectedCommand: '',
      loading: true,
      editOpModalOpen: false,
      modalInfo: null,
      states: ['Active', 'Inactive'],
      stateActive: null, // change to whatever info is coming in
      ignoreEmailText: '',
      ignoreEmails: [], // change to whatever info is coming in
      hasProducts: false, // change to whatever info is coming in
      allForms: null,
      allMeetingWorkflows: null,
      selected_org: null,
      old_selected_org: null,
      page: null,
      orgForms: null,
      orgMeetingWorkflows: null,
      organizations: CollectionManager.create({ ModelClass: Organization }),
    }
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  mounted() {
    console.log('mounted', this.hasProducts)
  },
  methods: {
    test() {
      console.log('test', this.hasProducts)
    },
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.allForms = res
        console.log('getAllForms', this.allForms[0])
      } catch (e) {
        console.log(e)
      }
    },
    async getAllMeetingWorkflows() {
      try {
        let res = await MeetingWorkflows.api.getMeetingList()
        this.allMeetingWorkflows = res.results
      } catch (e) {
        console.log(e)
      }
    },
    async runCommand() {
      try {
        const res = await User.api.callCommand(this.selectedCommand.value).then((res) => {
          this.$Alert.alert({
            type: 'success',
            timeout: 1000,
            message: res['message'],
          })
        })
      } catch (e) {
        console.log(e)
      }
    },
    ignoreEmail() {
      if (!this.checkEmail()) {
        return console.log('Please enter a valid email')
      }
      this.ignoreEmails.push(this.ignoreEmailText);
      this.ignoreEmailText = '';
      console.log('ignoreEmails', this.ignoreEmails);
    },
    checkEmail() {
      let symbol = false;
      let dot = false;
      for (let i = 0; i < this.ignoreEmailText.length; i++) {
        if (!symbol) {
          if (this.ignoreEmailText[i] === '@') {
            symbol = true;
          }
        } else if (!dot) {
          if (this.ignoreEmailText[i] === '.') {
            dot = true;
          }
        } else {
          return true;
        }
      }
      return false;
    },
    goBack() {
      this.selected_org = this.old_selected_org;
      this.old_selected_org = null;
      this.page = null;
    },
    goToUser() {
      if (!this.selectedUsers || !this.selectedUsers.length) {
        return;
      }
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'Users';
    },
    goToSlackForm() {
      if (!this.selectedSlackForms || !this.selectedSlackForms.length) {
        return;
      }
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'SlackForm';
    },
    goToMeetingWorkflow() {
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'MeetingWorkflow';
    },
    openModal(meetingWorkflow) {
      this.modalInfo = meetingWorkflow;
      this.editOpModalOpen = true;
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
    },
    slackFormLabel({formType, resource}) {
      let formattedFormType = formType[0];
      for (let i = 1; i < formType.length; i++) {
        formattedFormType += formType[i].toLowerCase();
      }
      return `${formattedFormType} ${resource}`;
    },
    filterOrgForms(org_id) {
      return this.allForms.filter((form) => form.organization == org_id)
    },
    filterMeetingWorkflow(org_id) {
      return this.allMeetingWorkflows.filter((workflow) => workflow.org_ref.id == org_id)
    },
    showOrgData(org_id) {
      this.orgForms = this.filterOrgForms(org_id)
      this.orgMeetingWorkflows = this.filterMeetingWorkflow(org_id)
    },
    filterUsers(org_id) {
      return this.allUsers.list.filter((user) => user.organization == org_id)
    },
    filterSlackForms(org_id) {
      return this.allForms.filter((form) => form.organization == org_id)
    },
  },
  created() {
    this.getAllForms()
    this.getAllMeetingWorkflows()
    this.organizations.refresh()
    this.allUsers.refresh()
  },
  watch: {
    organizations() {
      if (this.selected_org) {
        this.selected_org.id = this.organizations[0].id
        this.orgUsers = this.filterUsers(this.selected_org.id)
        this.orgSlackForms = this.filterSlackForms(this.selected_org.id)
        this.orgMeetingWorkflows = this.filterMeetingWorkflow(this.selected_org.id)
        // console.log('this.orgSlackForms', this.orgSlackForms)
      }
    },
    selected_org() {
      if (this.selected_org) {
        this.showOrgData(this.selected_org.id)
        this.loading = false
        this.orgUsers = this.filterUsers(this.selected_org.id)
        this.orgSlackForms = this.filterSlackForms(this.selected_org.id)
        console.log('this.orgSlackForms', this.orgSlackForms)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.staff {
  margin-top: 3rem;
  display: flex;
  height: 100vh;
}

.staff__drawer {
  width: 20vw;
  border-right: 1px solid black;
}

.staff__main_page {
  width: 70vw;
}

p {
  font-size: 14px;
}
h1 {
  margin-top: -1px;
  margin-left: -0.1rem;
  font-size: 38px;
}
.form__list {
  display: flex;
  flex-wrap: wrap;
}
ul {
  margin: 0;
  padding: 0;
}
.form__list_item {
  padding: 0 2rem 2rem 2rem;
  border: 1px solid black;
  width: 20vw;
  margin: 1rem;
}
.sub_text {
  font-size: 12px;
  padding-left: 1rem;
}

.field__list_item {
  display: flex;
  flex-direction: column;
}

.command_dropdown {
  // margin: 2rem;
  display: flex;
}

.green_button {
  color: white;
  background-color: $dark-green;
  border-radius: 0.25rem;
  padding: 0.5rem 1rem;
  font-weight: bold;
  font-size: 12px;
  border: none;
  cursor: pointer;
}

.sized{
  height: 3em;
  align-self: center;
}

input[type='search'] {
  border: none;
  background-color: white;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
::placeholder {
  color: $very-light-gray;
}
.wide {
  display: flex;
  justify-content: center;
  width: 100%;
  background-color: white;
}
.user_title {
  margin-left: 1rem;
}
.user_item_container {
  border: 1px solid black;
  margin: 1rem;
  padding: .25rem 1rem;

  h3 {
    margin: 0;
  }

  h4 {
    margin: .25rem .5rem;
  }
}
.back {
  margin: 1rem;
  text-decoration: underline;
  cursor: pointer;
}
</style>