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
    <modal name="add-stage-modal" heading="Select a Stage" height="auto" :scrollable="true">
      <div class="modal-container">
        <div v-if="!loadingStages" class="modal-container__box">
          <div class="modal-container__box__header">
            <h2 class="modal-container__box__title">Select a stage</h2>
          </div>
          <div class="modal-container__box__content">
            <div class="box__content-select">
              
            </div>
          </div>

          <div class="modal-container__box__footer mar">
            <div class="centered">
              <span class="user-message" v-if="!stages.length">
                <small>Can't see your stages?</small>
              </span>
              <span v-else class="user-message">
                <small>Recently updated your stages?</small>
              </span>
              <PulseLoadingSpinnerButton
                @click="() => refreshFormStages()"
                :loading="false"
                class="stage__button"
                text="Refresh"
              />
            </div>
            <div class="centered">
              <button
                style="margin-top: 1rem"
                class="modal-container__box__button"
                @click="
                  () => {
                    $modal.hide('add-stage-modal'),
                      addForm(this.selectedStage),
                      selectForm('Opportunity', 'STAGE_GATING', selectedStage)
                  }
                "
                :disabled="!this.selectedStage"
              >
                Select
              </button>
            </div>
          </div>
        </div>
        <div v-else>LOADING</div>
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
      <div
        v-if="stageDropDownOpen && resource == 'Opportunity'"
        :class="selectedStage ? 'small__stage__dropdown' : 'stage__dropdown'"
      >
        <div>
          <div class="stage__dropdown__header">Your Stage Gate Forms</div>
          <div
            v-for="(form, i) in formStages"
            :key="i"
            class="stage__dropdown__stages__container"
            :class="{
              'stage__dropdown__stages__container--selected':
                selectedForm &&
                selectedForm.formType == 'STAGE_GATING' &&
                selectedForm.resource == 'Opportunity' &&
                selectedForm.stage == form.stage,
            }"
          >
            <div
              class="stage__dropdown__stages__title"
              @click="selectForm('Opportunity', 'STAGE_GATING', form.stage)"
            >
              {{ form.stage }}
            </div>
            <div class="stage__dropdown__stages__x" @click.prevent="deleteForm(form)">x</div>
          </div>
        </div>
        <div style="display: flex; justify-content: center">
          <button @click="onAddForm" class="modal-container__box__button">Add Form</button>
        </div>
      </div>

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
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import Paginator from '@thinknimble/paginator'
import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CustomSlackForm from '@/views/settings/CustomSlackForm'
import { mapState } from 'vuex'
import SlackOAuth, { salesforceFields } from '@/services/slack'
import { SObjectField, SObjectValidation, SObjectPicklist } from '@/services/salesforce'
import { SOBJECTS_LIST } from '@/services/salesforce'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'SlackFormSettings',
  components: { CustomSlackForm, PulseLoadingSpinnerButton, Paginator },
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

.box-updated__header {
  &:hover {
    cursor: pointer;
    background-color: #f4f5f6;
  }
}

.box-updated__tab {
  display: flex;
  padding: 0;

  justify-content: center;
}
.box-updated__tab-header {
  padding: 0 2rem;

  width: 100%;
  display: flex;
}
.box__tab-button {
  > .button {
    height: 100%;
  }
  position: absolute;
  right: 3rem;
  height: 3rem;
}
.box-updated__content {
  display: none;

  &--closed {
    animation: closemenu forwards;
    animation-duration: 0.5s;
    animation-iteration-count: 1;
    display: block;
  }
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
.stage__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  font-weight: bold;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $dark-green;
  cursor: pointer;
  font-weight: bold;
  font-size: 1.02rem;
}
.modal-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-top: 1rem;
  border-radius: 0.25rem;
  background-color: $panther;
  &__box {
    &__title {
      text-align: center;
      margin: 2rem 0;
      width: 100%;
    }
    &__content {
      display: flex;
      justify-content: center;
      min-height: 20rem;
    }
    &__button {
      @include primary-button();
    }
  }
}

.box__footer {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
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

.header {
  &__container {
    display: flex;
    justify-content: center;
    flex-direction: column;
    align-items: center;
    font-size: 1.25rem;
    padding-top: 2rem;
  }
  &__list {
    display: flex;
    flex-direction: column;
    text-align: left;
    margin-bottom: 1rem;

    &__item {
      font-size: 18px;
    }
  }
}
.field-title {
  font-size: 0.85rem;
  margin-left: 1rem;

  &__bold {
    font-family: #{$bold-font-family};
    margin: 2rem 0 0 1rem;
  }
}

.search-bar {
  @include input-field();
  height: 2.5rem !important;
  width: 13rem;
  padding: 0 0 0 1rem;
  margin: 1rem;
}

.paginator {
  @include paginator();
  &__container {
    border: none;
    display: flex;
    justify-content: flex-start;
    width: 11rem;
    font-size: 0.75rem;
    margin-top: 1rem;
  }
  &__text {
    width: 6rem;
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
.small__stage__dropdown {
  margin-bottom: 70vh;
  margin-left: 80vw;
  padding: 6px 0 14px;
  border-radius: 0.5rem;
  box-shadow: 0 5px 10px 10px rgba(0, 0, 0, 0.5);
  background-color: $panther;
  position: absolute;
  z-index: 100;
  overflow-y: scroll;
}
.stage {
  &__container {
    position: relative;
  }
  &__dropdown {
    margin-top: 16rem;
    width: 30vw;

    padding: 6px 0 14px;
    border-radius: 0.5rem;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    background-color: $panther;
    position: absolute;

    z-index: 100;
    overflow-y: scroll;

    &__header {
      font-size: 1.25rem;
      padding: 0.5rem;
      border-bottom: solid 2px #9e9ea6;
      cursor: move;
      z-index: 10;
    }
    &__stages {
      &__container {
        display: flex;

        height: 2.5rem;
        padding: 0.75rem;
        font-size: 0.75rem;
        cursor: pointer;
        align-items: center;

        &--selected {
          color: white;
          background-color: #{$dark-green};
        }
      }
      &__title {
        font-size: 12;
        font-family: #{$bold-font-family};
        cursor: pointer;

        width: 100%;
      }
      &__x {
        z-index: 1000;
      }
    }
  }
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
.resources {
  padding-top: 0.5rem;
  display: flex;
  justify-content: center;
}
.tip-continue {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding-top: 2rem;
  margin-top: -1rem;
}

a {
  text-decoration: none;
  color: white;
}

.main__content {
  padding-top: 1rem;
}
.muted {
  color: #9f9cb7;
  font-size: 1rem;
  margin-top: -5px;
}
.hint {
  color: $base-gray;
  font-weight: 0.25rem;
  padding-left: 0.25rem;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  margin-bottom: 0.5em;
}
button {
  margin-top: 1em;
  border: none;
  text-align: center;
}
.buttons__ {
  height: 3rem;
  width: 13rem;
  text-align: center;
  border-radius: 0.5rem;
  border-bottom: 2px solid $theme-gray;
  color: $gray;
  background-color: white;
  font-weight: bolder;
  font-size: 0.975rem;
  margin-right: 1.5rem;
}
.buttons__:hover {
  color: #cc3873;
  border-bottom: 2px solid #cc3873;
  cursor: pointer;
}
.primary-button {
  padding: 1rem;
  border-radius: 0.5rem;
}
.primary-button:hover {
  transform: scale(1.025);
}
.mar {
  margin-bottom: 0.5rem;
}
.mar__ {
  margin-top: 1.5rem;
}
.activeTab {
  height: 3rem;
  width: 12.5rem;
  text-align: center;
  border-radius: 0.5rem;
  background-color: white;
  border-bottom: 2px solid #cc3873;
  color: #cc3873;
  font-weight: bolder;
  font-size: 0.975rem;
  margin-right: 1.5rem;
}
.search {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 3rem;
  margin-top: -1rem;
}
.search_buttons_row {
  display: flex;
  flex-direction: column;
  margin-top: 1rem;
}
.objects__ {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin: 1rem;
}
.col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-bottom: 1rem;
}
.mar__top {
  margin-top: 7rem;
}
.purple {
  color: $grape;
  font-size: 18px;
}
img {
  margin-right: 0.25rem;
  margin-top: 0.5rem;
}
.centered {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}
</style>
