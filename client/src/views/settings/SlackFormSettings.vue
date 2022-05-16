<template>
  <div class="container">
    <modal name="required-modal" heading="Select a Stage">
      <div class="required__container">
        <img
          class="tooltip image"
          src="@/assets/images/tooltipgray.png"
          @click="toggleRequiredModal"
        />
        <div class="required__title">Required Fields</div>
        <div class="required__instructions">
          Below are your company’s validation rules for this object. These are fields that have been
          pre-filled as part of the form for this resource. Additional Validations may apply for
          your Salesforce Resources
        </div>
        <div class="required__content__container">
          <div v-for="(validation, k) in validations.list" :key="k">
            <div class="required__title">{{ validation.description }}</div>
            <div class="required__content">{{ validation.message }}</div>
          </div>
        </div>

        <Paginator
          v-if="validations.pagination.next || validations.pagination.previous"
          :pagination="validations.pagination"
          @next-page="nextValidation"
          @previous-page="previousValidation"
          :loading="validations.loadingNextPage"
          arrows
          size="small"
          class="popup-paginator"
        />
      </div>
    </modal>
    <h1
      v-if="selectedStage"
      style="color: black; padding-bottom: 0.5rem; border-bottom: 3px solid #199e54"
    >
      {{ selectedStage }} Form
    </h1>
    <h1 v-else style="color: black; padding-bottom: 0.5rem; border-bottom: 3px solid #199e54">
      Stage Specific Forms
    </h1>

    <div class="centered__stage">
      <template v-if="selectedForm">
        <div class="box__content--expanded">
          <CustomSlackForm
            :show-validations="showValidations"
            :formType="formType"
            :customForm="selectedForm"
            :resource="resource"
            v-on:update:selectedForm="updateForm($event)"
            :loading="formFields.refreshing"
            :stageForms="formStages"
            :managrFields="publicFields"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import Paginator from '@thinknimble/paginator'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CustomSlackForm from '@/views/settings/CustomSlackForm'
import { mapState } from 'vuex'
import SlackOAuth from '@/services/slack'
import { SObjectField, SObjectValidation, SObjectPicklist } from '@/services/salesforce'
import { SOBJECTS_LIST } from '@/services/salesforce'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'SlackFormSettings',
  components: { CustomSlackForm, Paginator },
  data() {
    return {
      ...FORM_CONSTS,
      SOBJECTS_LIST,
      allForms: [],
      allFields: [],
      publicFields: [],
      formsByType: [],
      isLoading: false,
      selectedTab: null,
      resource: null,
      selectedForm: null,
      showValidations: false,
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
      stageDropDownOpen: true,
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
      this.publicFields = await SObjectField.api.getPublicFields()
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
    async refreshFormStages() {
      try {
        const res = await SObjectPicklist.api.getStagePicklistValues()

        if (res.status == 200) {
          this.$Alert.alert({
            type: 'success',
            timeout: 2000,
            message: 'Successfully Retrieved Picklist Values please refresh your page',
          })
        }
      } catch {
        this.$Alert.alert({
          type: 'error',
          timeout: 2000,
          message: 'There was an error collecting stages',
        })
      } finally {
        this.loadingStages = false
      }
    },

    nextValidation() {
      this.validations.nextPage()
    },
    previousValidation() {
      this.validations.prevPage()
    },

    toggleRequiredModal() {
      this.$modal.show('required-modal')
    },

    async selectForm(resource, formType, stage = '') {
      this.selectedForm = this.allForms.find(
        (f) => f.resource == resource && f.formType == formType && f.stage == stage,
      )
      this.formType = formType
      this.selectedStage = stage
    },

    async listFields(query_params = {}) {
      try {
        this.formFields.filters = query_params
        this.formFields.refresh()
      } catch {
        this.$Alert.alert({
          message: 'There was an error gathering fields',
          type: 'error',
          timeout: 3000,
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

    async listPicklists(query_params = {}) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.stages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },

    async deleteForm(form) {
      if (form.id && form.id.length) {
        const id = form.id

        SlackOAuth.api
          .delete(id)
          .then(async (res) => {
            this.$Alert.alert({
              type: 'success',

              message: 'Form deleted successfully',

              timeout: 2000,
            })

            const forms = this.formsByType.filter((f) => {
              return f.id !== form.id
            })
            this.fallForms = [...forms]
          })

          .catch((e) => {
            this.$Alert.alert({
              type: 'error',

              message: 'There was an error, please try again',

              timeout: 2000,
            })
          })

          .finally(() => {})
      } else {
        const forms = this.allForms.filter((f) => {
          return f.id !== form.id
        })
        this.allForms = [...forms]
        console.log(this.allForms)
      }
    },

    async onAddForm() {
      this.$modal.show('add-stage-modal')
      this.loadingStages = true
      try {
        await this.listPicklists({ salesforceObject: this.Opportunity, picklistFor: 'StageName' })
      } catch (e) {
        this.$modal.close('add-stage-modal')
        this.$Alert.alert({ message: 'Failed to retrieve stages', timeout: 3000 })
      } finally {
        this.loadingStages = false
      }
    },
    addForm(stage) {
      /** Method for Creating a new stage-gating form, this is only available for Opportunities at this time */

      if (this.currentStagesWithForms.includes(stage)) {
        return this.$Alert.alert({
          message: 'This Stage already has a form',
          timeout: 5000,
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

    updateForm(event) {
      this.selectedForm = event
      let index = this.allForms.findIndex((f) => f.id == this.selectedForm.id)

      if (~index) {
        this.allForms[index] = this.selectedForm
        this.allForms = [...this.allForms]
      }
    },
  },
  beforeMount() {
    this.resource = 'Opportunity'
    this.formType = 'STAGE_GATING'
    // this.resource = OPPORTUNITY
    // this.formType = STAGE_GATING
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
@import '@/styles/buttons';

.container {
  margin-top: 4rem;
  color: white;
  display: flex;
  align-items: center;
  flex-direction: column;
}
.box__content--expanded {
  max-height: 90vh;
  display: block;
  animation: expandmenu forwards;
  animation-duration: 1.5s;
  animation-iteration-count: 1;
  overflow-y: scroll;
  margin: 0 4em;
  padding-top: 2rem;
}

@keyframes expandmenu {
  0% {
    height: 0rem;
    opacity: 0;
  }
  100% {
    height: 50rem;
    opacity: 1;
  }
}

@keyframes closemenu {
  0% {
    display: block;
    height: 50rem;
    opacity: 0.01;
  }
  100% {
    display: none;
    height: 0rem;
    opacity: 0;
  }
}
.popup-paginator {
  @include paginator();
}
.centered__stage {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  height: 100%;
}

.tooltip {
  height: 1rem;
  margin: 1rem;
}

.required {
  &__container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__title {
    font-family: #{$bold-font-family};
    border-bottom: 2px solid #cc3873;
  }
  &__instructions {
    padding: 1.5rem 4.5rem;
    margin-bottom: 2rem;
  }

  &__content {
    margin: 1rem 0 2rem 0;
    &__container {
      width: 100%;
      padding: 1rem 3rem;
    }
  }
}
a {
  text-decoration: none;
  color: white;
}
button {
  margin-top: 1em;
  border: none;
  text-align: center;
}
img {
  margin-right: 0.25rem;
  margin-top: 0.5rem;
}
</style>
