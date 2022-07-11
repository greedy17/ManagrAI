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

    <h3 style="text-align: center" v-if="selectedStage">
      <span style="color: #41b883; margin-left: 0.25rem">{{ selectedStage }}</span> Validation Rules
    </h3>
    <div class="header" v-else-if="!selectedStage && !showLoader">
      <h3>Validation Rules</h3>
      <p>Apply additional fields to stages</p>
    </div>
    <div v-if="selectingStage">
      <div class="modal-container">
        <div class="modal-container__header">
          <h3>Select a stage</h3>
        </div>
        <div class="modal-container__body">
          <Multiselect
            :placeholder="selectedStage ? selectedStage : 'Select Stage'"
            @input="setStage($event)"
            :options="stages"
            openDirection="below"
            style="width: 20vw"
            selectLabel="Enter"
            track-by="value"
            label="label"
          >
            <template slot="noResult">
              <p class="multi-slot">No results.</p>
            </template>

            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.svg" alt="" />
                {{ selectedStage ? selectedStage : 'Select Stage' }}
              </p>
            </template>
          </Multiselect>
        </div>
        <div>
          <div style="display: flex; justify-content: flex-end; align-items: center">
            <div
              style="
                display: flex;
                justify-content: center;
                align-items: center;
                margin-right: -1rem;
              "
            >
              <p style="font-size: 11px">Dont see your stages ? Try refreshing</p>
              <PulseLoadingSpinnerButton
                @click="() => refreshFormStages()"
                :loading="loadingStages"
                class="modal-container__box__button"
                text="Refresh"
              />
            </div>

            <button
              class="modal-container__box__button"
              @click="
                () => {
                  this.selectingStage = !this.selectingStage
                  this.addingStage = !this.addingStage
                  addForm(this.selectedStage),
                    selectForm('Opportunity', 'STAGE_GATING', selectedStage)
                }
              "
              :disabled="!this.selectedStage"
            >
              Continue
            </button>
          </div>
        </div>
      </div>
    </div>

    <div :key="route_name_key" class="centered__stage">
      <template v-if="selectedForm">
        <div class="box__content--expanded">
          <CustomSlackForm
            :formType="formType"
            :customForm="selectedForm"
            :resource="resource"
            v-on:update:selectedForm="updateForm($event)"
            :loading="formFields.refreshing"
            :stageForms="formStages"
            :managrFields="publicFields"
            @cancel-selected="changeSelected"
          />
        </div>
      </template>

      <div class="center-loader" v-if="showLoader">
        <Loader loaderText="Gathering your validations rules" />
      </div>

      <div
        style="margin-top: 1rem"
        v-if="
          !selectingStage &&
          !addingStage &&
          resource == 'Opportunity' &&
          !selectedStage &&
          !showLoader
        "
        class="stage__dropdown"
      >
        <div class="stage__dropdown__header">
          {{ formLength ? 'Saved Validation Rules' : 'No Saved Validation Rules' }}
        </div>
        <div
          v-for="form in formStages"
          :key="form.stage"
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

          <div class="img-border" @click.prevent="deleteForm(form)">
            <img src="@/assets/images/trash.svg" class="invertTrash" alt="" />
          </div>
        </div>

        <div style="display: flex; justify-content: center; margin-top: 1rem">
          <button @click="onAddForm" class="modal-container__box__button">Add</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
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
  components: {
    CustomSlackForm,
    PulseLoadingSpinnerButton,
    Paginator,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
  },
  data() {
    return {
      ...FORM_CONSTS,
      selectedStage: null,
      SOBJECTS_LIST,
      allForms: [],
      allFields: [],
      publicFields: [],
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
      showLoader: true,
      formType: null,
      search: '',
      fieldParam: null,
      loading: false,
      formFields: CollectionManager.create({ ModelClass: SObjectField }),
      stageDropDownOpen: true,
      selectingStage: false,
      addingStage: false,
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
    formLength() {
      return this.formStages.length
    },
    route_name_key() {
      return this.$route.path + '/' + this.language
    },
  },
  methods: {
    logForm(i) {
      console.log(i)
    },
    changeSelected() {
      this.selectedForm = null
      this.selectingStage = !this.selectingStage
    },
    setStage(n) {
      this.selectedStage = n.value
    },
    async refreshFormStages() {
      this.loadingStages = true
      try {
        const res = await SObjectPicklist.api.getStagePicklistValues()
        if (res.status == 200) {
          this.$toast('Successfully Retrieved Picklist Values please refresh your page', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } catch {
        this.$toast('There was an error collecting stages.', {
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
            const forms = this.formsByType.filter((f) => {
              return f.id !== form.id
            })
            this.allForms = [...forms]
            this.logForm(form)
            this.$router.go()
          })

          .catch((e) => {
            this.$toast('Error, please try again', {
              timeout: 2000,
              position: 'top-left',
              type: 'error',
              toastClassName: 'custom',
              bodyClassName: ['custom'],
            })
          })

          .finally(() => {})
      } else {
        const forms = this.allForms.filter((f) => {
          return f.id !== form.id
        })
        this.allForms = [...forms]
      }
    },

    async onAddForm() {
      this.selectingStage = !this.selectingStage
      this.loadingStages = true
      try {
        await this.listPicklists({ salesforceObject: this.Opportunity, picklistFor: 'StageName' })
      } catch (e) {
        this.$modal.close('add-stage-modal')
        this.$toast('Failed to retreive stages', {
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
  },
  mounted() {
    setTimeout(() => {
      this.showLoader = false
    }, 500)
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

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1.25rem;
    padding-right: 0.25rem;
    padding-bottom: 0.5rem;
    filter: invert(70%);
  }
}
.invertTrash {
  filter: invert(20%);
}
.multi-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  color: $gray;
  font-size: 12px;
  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  cursor: text;
}
.img-border {
  display: flex;
  align-items: center;
  justify-content: center;

  border-radius: 0.2rem;
  cursor: pointer;

  img {
    height: 1rem;
    filter: invert(20%);
  }
}
.header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 100%;

  p {
    font-size: 14px;
    color: $gray;
  }
}
@keyframes dotFlashing {
  0% {
    background-color: $dark-green;
  }
  50%,
  100% {
    background-color: $lighter-green;
  }
}
.center-loader {
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  width: 80vw;
}
.container {
  color: $base-gray;
  display: flex;
  margin: 0px 120px;
  justify-content: center;
  align-items: flex-start;
  flex-direction: column;
  height: 100%;
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
.modal-container {
  min-height: 50vh;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin-top: 1rem;
  border-radius: 0.3rem;
  background-color: $white;
  color: $base-gray;
  width: 82vw;
  border: 1px solid #e8e8e8;

  &__header {
    padding: 0.1rem 1rem;
    border-bottom: 1px solid #e8e8e8;
    font-weight: 400;
  }
  &__body {
    height: 20vh;
    display: flex;
    justify-content: center;
  }
  &__box {
    &__button {
      font-size: 14px;
      border-radius: 0.3rem;
      cursor: pointer;
      background-color: $dark-green;
      color: $white;
      padding: 0.5rem 1.5rem;
      margin: 1rem;
    }
  }
}
button:disabled {
  font-size: 14px;
  border-radius: 0.3rem;
  cursor: pointer;
  background-color: $soft-gray;
  color: $gray;
  padding: 0.5rem 1.5rem;
  margin: 1rem;
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
  align-items: flex-start;
  flex-direction: row;
  height: 100%;
}

.stage {
  &__dropdown {
    min-height: 40vh;
    width: 82vw;
    border-radius: 0.3rem;
    border: 1px solid #e8e8e8;
    background-color: $white;
    overflow-y: scroll;

    &__header {
      font-size: 16px;
      padding: 1rem;
      border-bottom: 1px solid #e8e8e8;
    }
    &__stages {
      &__container {
        display: flex;
        border: 1px solid #e8e8e8;
        width: 99%;
        padding: 0rem 0.4rem 0.2rem 0.3rem;
        font-weight: 400;
        margin: 0.25rem;
        border-radius: 0.3rem;
        font-size: 14px;
        cursor: pointer;
        align-items: center;
        justify-content: flex-start;

        &--selected {
          color: $dark-green;
        }
      }
      &__title {
        cursor: pointer;
        padding: 0.2rem;
        margin-bottom: 0.2rem;
        margin-top: 0.5rem;
        width: 100%;
      }
      &__title:hover {
        color: $dark-green;
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
