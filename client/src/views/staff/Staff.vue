<template>
  <div class="staff">
    <div class="staff__drawer">
      <h1>Organizations</h1>
      <!-- <div :key="i" v-for="(org, i) in organizations.list">
        <div>{{org}}</div>
        <h2 @click="selected_org = org.id">{{ org.name }}</h2>
      </div> -->
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
            <button class="green_button" @click="runCommand">Enter</button>
          </div>

          <!-- <div class="form__list">
            <div :key="i" class="form__list_item" v-for="(form, i) in orgForms">
              <h3>{{ form.formType }} {{ form.resource }}</h3>
              <p>Form Fields:</p>
              <ul v-if="form.fieldsRef.length > 1">
                <li class="field__list_item" :key="i" v-for="(field, i) in form.fieldsRef">
                  <span>{{ field.order }}-{{ field.label }}</span
                  ><span class="sub_text">{{ field.dataType }}</span>
                </li>
              </ul>
              <p v-else>Form is not created</p>
            </div>
          </div> -->

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
        <div v-for="(user) in selectedUsers" :key="user.id">
          <h3>Full Name: {{user.fullName}}</h3>
          <h3>Email: {{user.email}}</h3>
          <h3>Role: {{user.role}}</h3>
        </div>
      </template>
      <template v-else-if="page === 'SlackForm'">
        <div v-for="(slackForm) in selectedSlackForms" :key="slackForm.id">
          <h3>{{slackForm.stage}}</h3>
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
    console.log('mounted', this.allForms)
  },
  methods: {
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
    goToUser(user) {
      if (!this.selectedUsers) {
        return;
      }
      console.log('user', user[0])
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'Users';
    },
    goToSlackForm() {
      if (!this.selectedSlackForms) {
        return;
      }
      this.old_selected_org = this.selected_org;
      this.selected_org = null;
      this.page = 'SlackForm';
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
  margin: 2rem;
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
</style>