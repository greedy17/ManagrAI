<template>
  <div class="display-flex-container">
    <div class="left-bar">
      <ConfigureLeftBar 
      :configPage="configPage" 
      :changeConfigPage="changeConfigPage" 
      :forms="allForms"
    />
    </div>
    <div class="main-content">
      <div v-if="configPage === 'integrations'">
        <ConfigureIntegrations />
      </div>
      <div v-else-if="configPage === 'forms'">
        <ConfigureForms
        :formType="UPDATE"
        :customForm="
          (this.selectedForm = this.allForms.find(
            (f) => f.resource == currentResource && f.formType == UPDATE,
          ))
        "
        :updateAllForms="updateAllForms"
        :resource="currentResource"
        v-on:update:selectedForm="updateForm($event)"
        :loading="formFields.refreshing"
        :stageForms="formStages"
        />
      </div>
      <div v-else-if="configPage === 'notes'">
        <ConfigureSync />
      </div>
      <div v-else-if="configPage === 'sync'">
        <ConfigureSync />
      </div>
      <div v-else-if="configPage === 'workflows'">
        <ConfigureAlerts :config="userCRM === 'HUBSPOT' ? allConfigs.DEAL_REVIEW_HUBSPOT : allConfigs.DEAL_REVIEW" />
      </div>
      <div v-else>
        <div>
          <h2>Error loading page. Please try again later.</h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ConfigureLeftBar from './ConfigureLeftBar.vue'
import ConfigureIntegrations from './ConfigureIntegrations.vue'
import ConfigureForms from './ConfigureForms.vue'
import ConfigureSync from './ConfigureSync.vue'
import ConfigureWorkflows from './ConfigureWorkflows.vue'
import ConfigureAlerts from './ConfigureAlerts.vue'
import { SObjectPicklist } from '@/services/salesforce'
import SlackOAuth from '@/services/slack'
import { CollectionManager } from '@thinknimble/tn-models'
import { ObjectField } from '@/services/crm'
import * as FORM_CONSTS from '@/services/slack'
import allConfigs from '@/views/settings/alerts/configs'

export default {
  name: 'ConfigureModal',
  props: {

  },
  components: {
    ConfigureLeftBar,
    ConfigureIntegrations,
    ConfigureForms,
    ConfigureSync,
    ConfigureWorkflows,
    ConfigureAlerts,
  },
  data() {
    return {
      ...FORM_CONSTS,
      allConfigs,
      configPage: 'integrations',
      currentResource: '',
      formFields: CollectionManager.create({ ModelClass: ObjectField }),
      stages: [],
      formStages: [],
      allForms: [],
      allFields: [],
    }
  },
  async created() {
    try {
      if (this.userCRM === 'HUBSPOT') {
        this.currentResource = this.DEAL
      } else if (this.userCRM === 'SALESFORCE') {
        this.currentResource = this.OPPORTUNITY
      }
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      console.log('allForms', this.allForms)
      this.allFields = await this.listFields()
      await this.listPicklists({
        salesforceObject: this.currentResource,
        picklistFor: 'StageName',
      })
    } catch (error) {
      console.log(error)
    }

    // users can only create one form for the stage orderd by stage

    this.getStageForms()
  },
  methods: {
    changeConfigPage(page) {
      this.configPage = page
    },
    async listPicklists(query_params = {}) {
      try {
        let res
        if (this.userCRM === 'HUBSPOT') {
          const form = this.allForms.find(
            (f) => f.resource == this.currentResource && f.formType == this.UPDATE,
          )
          const hsPicklist = form.fieldsRef.filter(
            (item) => query_params.picklistFor === item.apiName,
          )
          this.stages = hsPicklist && hsPicklist[0] ? hsPicklist[0].options : []
        } else if (this.userCRM === 'SALESFORCE') {
          res = await SObjectPicklist.api.listPicklists(query_params)
          this.stages = res.length ? res[0]['values'] : []
        }
      } catch (e) {
        console.log(e)
      }
    },
    async listFields(query_params = {}) {
      try {
        this.formFields.filters = query_params
        this.formFields.refresh()
      } catch {
        this.$toast('Error gathering fields', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      }
    },
    getStageForms() {
      // users can only create one form for the stage orderd by stage
      let forms = []
      this.stages.forEach((s) => {
        this.allForms
          .filter((f) => f.formType == this.STAGE_GATING)
          .forEach((sf) => {
            if (sf.stage == s.value) {
              forms.push(sf)
            }
          })
      })

      this.formStages = [...forms]
    },
    updateAllForms(forms) {
      this.allForms = forms
    }
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
@import '@/styles/modals';

.display-flex-container {
  display: flex;
  flex-direction: row;
  height: 90vh;
  overflow-y: hidden;
}

.test {
  border: 1px solid red;
}

.left-bar {
  width: 15%;
  // position: relative;
  // top: 0;
}
.main-content {
  width: 85%;
  overflow-y: auto;
}
</style>