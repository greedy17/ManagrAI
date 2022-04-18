<template>
  <div class="staff">
    <div class="staff__drawer">
      <div :key="i" v-for="(org, i) in organizations.list">
        <h2 @click="this.selected_org = org.id">{{ org.name }}</h2>
      </div>
    </div>
    <div class="staff__main_page">
      <template v-if="selected_org">
        <div class="form__list">
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
            <p>{{ 'event_data' in workflow.meeting_ref ? 'Google Meet' : 'Zoom Meeting' }}</p>
            <p>{{ workflow.meeting_ref.participants }}</p>
            <p>{{ workflow }}</p>
          </div>
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

export default {
  name: 'Staff',
  data() {
    return {
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
        console.log(this.allMeetingWorkflows)
      } catch (e) {
        console.log(e)
      }
    },
    filterOrgForms(org_id) {
      return this.allForms.map((form) => form.organization == org_id)
    },
    filterMeetingWorkflow(org_id) {
      return this.allMeetingWorkflows.map((workflow) => workflow.org_ref.id == org_id)
    },
    showOrgData(org_id) {
      this.orgForms = this.filterOrgForms(org_id)
      this.orgMeetingWorkflows = this.filterMeetingWorkflow(org_id)
    },
  },
  created() {
    this.getAllForms()
    this.getAllMeetingWorkflows()
    this.organizations.refresh()
  },
  watch: {
    organizations() {
      this.selected_org = organizations[0].id
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
</style>