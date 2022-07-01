<template>
  <div class="update_opportunity">
    <div class="opportunity_title">
      <h3>Create Leads</h3>
      <p style="color: #5d5e5e; margin-top: -0.5rem; font-size: 0.95rem">
        Select the Fields you’d like to display when creating Leads via Slack
      </p>
    </div>
    <div class="box__content--expanded">
      <CustomSlackForm
        :formType="CREATE"
        :customForm="
          (this.selectedForm = this.allForms.find(
            (f) => f.resource == LEAD && f.formType == CREATE,
          ))
        "
        :resource="LEAD"
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
  name: 'CreateLeads',
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
      LEAD: 'Lead',
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
    currentStagesWithForms() {
      return this.formStages.map((sf) => sf.stage)
    },
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
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.stages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
  },
  async onAddForm() {
    this.$modal.show('add-stage-modal')
    this.loadingStages = true
    try {
      await this.listPicklists({ salesforceObject: this.Opportunity, picklistFor: 'StageName' })
    } catch (e) {
      this.$modal.close('add-stage-modal')
      this.$toast('Failed to retrieve stages', {
        timeout: 2000,
        position: 'top-left',
        type: 'error',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    } finally {
      this.loadingStages = false
    }
  },
  addForm(stage) {
    /** Method for Creating a new stage-gating form, this is only available for Opportunities at this time */

    if (this.currentStagesWithForms.includes(stage)) {
      this.$toast('This stage already has a form', {
        timeout: 2000,
        position: 'top-left',
        type: 'default',
        toastClassName: 'custom',
        bodyClassName: ['custom'],
      })
    }
    let newForm = SlackOAuth.customSlackForm.create({
      resource: this.OPPORTUNITY,
      formType: this.STAGE_GATING,
      stage: stage,
    })
    newForm.fieldsRef = this.formStages.reduce((acc, curr) => {
      let fields = curr.fieldsRef.filter((f) => !acc.map((af) => af.id).includes(f.id))
      acc = [...acc, ...fields]
      return acc
    }, [])
    this.allForms = [...this.allForms, newForm]
    this.getStageForms()
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
