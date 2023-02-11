<template>
  <div class="update_opportunity">
    <CustomSlackForm
      :formType="UPDATE"
      :customForm="
        (this.selectedForm = this.allForms.find(
          (f) => f.resource == currentResource && f.formType == UPDATE,
        ))
      "
      :resource="currentResource"
      v-on:update:selectedForm="updateForm($event)"
      :loading="formFields.refreshing"
      :stageForms="formStages"
    />
  </div>
</template>

<script>
import { CollectionManager } from '@thinknimble/tn-models'
import CustomSlackForm from '@/views/settings/CustomSlackForm'
import { mapState } from 'vuex'
import SlackOAuth from '@/services/slack'
import { SObjectPicklist } from '@/services/salesforce'
import { ObjectField } from '@/services/crm'
import { SOBJECTS_LIST } from '@/services/salesforce'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'Forms',
  components: { CustomSlackForm },
  data() {
    return {
      ...FORM_CONSTS,
      SOBJECTS_LIST,
      allForms: [],
      allFields: [],
      selectedForm: null,
      stages: [],
      formFields: CollectionManager.create({ ModelClass: ObjectField }),
      currentResource: '',
      formStages: [],
    }
  },
  watch: {},

  async created() {
    try {
      if (this.userCRM === 'HUBSPOT') {
        this.currentResource = this.DEAL
      } else if (this.userCRM === 'SALESFORCE') {
        this.currentResource = this.OPPORTUNITY
      }
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
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

  computed: {
    ...mapState(['user']),
    userCRM() {
      return this.$store.state.user.crm
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
      console.log(event)
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
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.update_opportunity {
  color: $base-gray;
  // overflow: auto;
  padding-left: 60px;
}
h3 {
  font-size: 1.35rem;
}
</style>
