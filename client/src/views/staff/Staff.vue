<template>
  <div class="staff">
    <div class="staff__drawer">
      <h1>Organizations</h1>
      <div :key="i" v-for="(org, i) in organizations.list">
        <h2 @click="selected_org = org.id">{{ org.name }}</h2>
      </div>
    </div>
    <div class="staff__main_page">
      <template v-if="selected_org">
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
          </div> -->
        </template>
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
      orgUsers: null,
      selectedCommand: '',
      loading: true,
      allForms: null,
      allMeetingWorkflows: null,
      selected_org: null,
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
    console.log(this.allUsers)
  },
  methods: {
    async getAllForms() {
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.allForms = res
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
  },
  created() {
    this.getAllForms()
    this.getAllMeetingWorkflows()
    this.organizations.refresh()
    this.allUsers.refresh()
  },
  watch: {
    organizations() {
      this.selected_org = this.organizations[0].id
      this.orgUsers = this.filterUsers(this.selected_org)
    },
    selected_org() {
      this.showOrgData(this.selected_org)
      this.loading = false
      this.orgUsers = this.filterUsers(this.selected_org)
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