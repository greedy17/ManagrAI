<template>
  <div class="pipelines">
    <div class="pipelines__center">
      </div>
      <div :key="i" v-for="(org, i) in organizations.list">
        <h1>{{ org.name }}</h1>  
        <div class="form__list">
            <template v-for="(form, i) in allForms">
                <div :key="i" class="form__list_item" v-if="org.id === form.organization">
                    <h3>{{form.formType}} {{form.resource}}</h3>
                    <p>Form Fields:</p>
                    <ul v-if="form.fieldsRef.length > 1">
                        <li class="field__list_item" :key="i" v-for="(field, i) in form.fieldsRef"><span>{{field.order}}-{{field.label}}</span><span class="sub_text">{{field.dataType}}</span></li>
                    </ul>
                    <p v-else>Form is not created</p>
                </div>
            </template>
        </div>
        <hr>
        <div class="form__List">
          <template v-for="(workflow, i) in allMeetingWorkflows">
            <div :key="i" class="form__list_item" v-if="org.id === workflow.org_ref.id">
              <p>{{workflow.meeting_ref.event_data.participants ? workflow.meeting_ref.event_data : workflow.meeting_ref.participants}}</p>
            </div>
          </template>
        </div>

      </div>
      
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
  },
  created() {
    this.getAllForms()
    this.getAllMeetingWorkflows()
    this.organizations.refresh()
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.pipelines {
  margin-top: 3rem;
  color: $base-gray;

  &__preview {
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    margin: 1rem 3rem;
    z-index: 2;
  }
  &__center {
    display: flex;
    align-items: flex-start;
    justify-content: space-evenly;
  }
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