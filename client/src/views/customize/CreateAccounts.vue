<template>
  <div class="update_opportunity">
    <div class="opportunity_title">
      <h3>Create Accounts</h3>
      <p style="color: #5d5e5e; margin-top: -0.5rem; font-size: 0.95rem">
        Select the Fields you’d like to display when creating Accounts via Slack
      </p>
    </div>
    <div class="box__content--expanded">
      <CustomSlackForm
        :formType="CREATE"
        :customForm="
          (this.selectedForm = this.allForms.find(
            (f) => f.resource == ACCOUNT && f.formType == CREATE,
          ))
        "
        :resource="ACCOUNT"
        v-on:update:selectedForm="updateForm($event)"
        :loading="formFields.refreshing"
        :stageForms="formStages"
      />
    </div>
  </div>
</template>

<script>
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CustomSlackForm from '@/views/settings/CustomSlackForm'
import { mapState } from 'vuex'
import SlackOAuth from '@/services/slack'
import { SObjectField, SObjectValidation, SObjectPicklist } from '@/services/salesforce'
import { SOBJECTS_LIST } from '@/services/salesforce'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CreateAccounts',
  components: { CustomSlackForm },
  data() {
    return {
      ...FORM_CONSTS,
      SOBJECTS_LIST,
      allForms: [],
      allFields: [],
      formsByType: [],
      isLoading: false,
      selectedTab: null,
      resource: null,
      selectedForm: null,
      newForms: [],
      selectedStage: null,
      selectedFormFields: [],
      stages: [],
      loadingStages: false,
      formType: null,
      search: '',
      fieldParam: null,
      loading: false,
      formFields: CollectionManager.create({ ModelClass: SObjectField }),
      stageDropDownOpen: false,
      isVisible: false,
      validations: CollectionManager.create({
        ModelClass: SObjectValidation,
        pagination: Pagination.create({ size: 2 }),
      }),
      formStages: [],
      started: false,
    }
  },
  async created() {
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      this.allFields = await this.listFields()
      await this.listPicklists({
        salesforceObject: this.Opportunity,
        picklistFor: 'StageName',
      })
    } catch (error) {
      console.log(error)
    }

    // users can only create one form for the stage orderd by stage

    this.getStageForms()
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
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
    updateForm(event) {
      this.selectedForm = event
      let index = this.allForms.findIndex((f) => f.id == this.selectedForm.id)

      if (~index) {
        this.allForms[index] = this.selectedForm
        this.allForms = [...this.allForms]
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
    async listPicklists(query_params = {}) {
      try {
        let res
        if (this.userCRM === 'HUBSPOT') {
          const hsPicklist = this.objectFields.list.filter(item => query_params.picklistFor === item.apiName)
          this.stages = hsPicklist && hsPicklist[0] ? hsPicklist[0].options : []
        } else if (this.userCRM === 'SALESFORCE') {
          res = await SObjectPicklist.api.listPicklists(query_params)
          this.stages = res.length ? res[0]['values'] : []
        }
      } catch (e) {
        console.log(e)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.update_opportunity {
  color: $base-gray;
  overflow: auto;
}
.opportunity_title {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 4.2rem;
  margin-top: 3rem;
}
h3 {
  font-size: 1.35rem;
}
</style>
