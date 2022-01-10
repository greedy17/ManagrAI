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

    <h3
      v-if="selectedStage"
      style="padding-bottom: 0.5rem; border-bottom: 3px solid #199e54; font-size: 1.65rem"
    >
      {{ selectedStage }}
    </h3>
    <h2 v-else>Apply additional fields to stages</h2>

    <!-- <modal name="objects-modal" heading="Select a Stage">
      <div class="objects__">
        <img class="tooltip image" src="@/assets/images/toolTip.png" @click="toggleObjectsModal" />
        <div class="required__title">Forms</div>
        <div>
          <p class="mar">
            <strong>Update:</strong>
            This form appears whenever you see the “Update” button
          </p>

          <p class="mar">
            <strong>Create:</strong>
            This form is triggered when you run the slack command, "managr-create"
          </p>
          <p class="mar">
            <strong>Stage Related Fields:</strong>
            Additional fields needed to advance Stages
          </p>
        </div>
      </div>
    </modal> -->

    <!-- <div class="header__container" v-if="!resource">
      <div class="col" style="margin-top: 4rem">
        <h3 class="header__title">Select a Salesforce Object</h3>
        <h3 class="muted">
          <strong style="font-size: 17px">Pro-tip:</strong> Start with the
          <strong style="font-size: 16px; color: #cc3873">Opportunity</strong> and
          <strong style="font-size: 16px; color: #cc3873">Contact</strong>
          objects, they are the most used.
        </h3>
      </div>
    </div> -->
    <div v-if="selectingStage">
      <div class="modal-container">
        <div style="text-align: center">
          <h3>Select a stage</h3>
          <div class="centered">
            <DropDownSearch
              :items.sync="stages"
              v-model="selectedStage"
              displayKey="label"
              valueKey="value"
              nullDisplay="Select a Stage"
              searchable
              local
            />
          </div>
        </div>
        <div>
          <div style="display: flex; justify-content: flex-end">
            <button
              :class="
                !this.selectedStage
                  ? 'modal-container__box__button'
                  : 'modal-container__box__button bouncy'
              "
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
              Select
            </button>
          </div>
        </div>

        <!-- <div class="centered">
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
          </div> -->
      </div>
    </div>

    <div class="centered__stage">
      <!-- <div @click.prevent="toggleSelectedFormResource(resource)" class="box-updated__header">
            <span class="box-updated__title">
              {{ resource }}
              <img
                v-if="selectedTab && isVisible"
                style="height: 1rem; margin-left: 1rem"
                src="@/assets/images/tooltipgray.png"
                @click.prevent.stop="toggleRequiredModal"
              />
            </span>
          </div> -->

      <!-- <div :class="resource ? 'search_buttons_row' : ''">
        <DropDownSearch
          :items.sync="SOBJECTS_LIST"
          v-model="resource"
          displayKey="key"
          valueKey="value"
          nullDisplay="Select salesforce object"
          class="search"
        />

        <div class="row">
          <div v-if="resource">
            <button
              @click="selectForm(resource, UPDATE)"
              class="buttons__"
              :class="this.formType == UPDATE ? 'activeTab' : 'buttons__'"
            >
              <img src="@/assets/images/edit.png" alt="update" />
              {{ ` Update ${resource}` }}
            </button>

            <button
              @click="selectForm(resource, CREATE)"
              :class="this.formType == CREATE ? 'activeTab' : 'buttons__'"
            >
              <img src="@/assets/images/create.png" alt="create" />
              {{ ` Create ${resource}` }}
            </button>
            <button
              @click="openStageDropDown"
              v-if="resource == OPPORTUNITY"
              :class="this.formType == STAGE_GATING ? 'activeTab' : 'buttons__'"
            >
              <img src="@/assets/images/stageStairs.png" alt="" />
              Stage Related Fields
            </button>
            <img
              style="cursor: pointer"
              src="@/assets/images/info.png"
              @click.prevent.stop="toggleObjectsModal"
            />
          </div>
        </div>
      </div> -->
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

      <div
        style="margin-top: 1rem"
        v-if="!selectingStage && !addingStage && resource == 'Opportunity' && !selectedStage"
        class="stage__dropdown"
      >
        <div>
          <!-- <div v-if="selectedStage">{{ selectedStage }} Form</div> -->
          <div class="stage__dropdown__header">
            {{ formStages.length ? 'Saved Validation Rules' : 'No Saved Validation Rules' }}
          </div>
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
              style="color: white"
              @click="selectForm('Opportunity', 'STAGE_GATING', form.stage)"
            >
              {{ form.stage }}
            </div>

            <div class="stage__dropdown__stages__x" @click.prevent="deleteForm(form)">
              <img src="@/assets/images/remove.png" style="height: 1rem" alt="" />
            </div>
          </div>
        </div>
        <div style="display: flex; justify-content: center; margin-top: 1rem">
          <button @click="onAddForm" class="modal-container__box__button">Add</button>
        </div>
      </div>
    </div>
    <!-- 
    <div class="tip-continue" v-if="resource">
      <button class="primary-button">
        <router-link :to="{ name: 'ListTemplates' }">Continue to Smart Alerts </router-link>
      </button>
    </div> -->
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
import DropDownSearch from '@/components/DropDownSearch'
import SObjectFormBuilderAPI, { SOBJECTS_LIST } from '@/services/salesforce'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'SlackFormSettings',
  components: { CustomSlackForm, PulseLoadingSpinnerButton, DropDownSearch, Paginator },
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
  watch: {},
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
    selectedFormType() {
      return this.selectedForm ? this.selectedForm.formType : null
    },

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

    nextPage() {
      this.formFields.nextPage()
    },
    previousPage() {
      this.formFields.prevPage()
    },
    nextValidation() {
      this.validations.nextPage()
    },
    previousValidation() {
      this.validations.prevPage()
    },
    async searchFields() {
      this.loading = true

      this.formFields.filters = {
        search: this.search,
        salesforceObject: this.resource,
        ...this.fieldParam,
      }
      this.formFields.refresh()

      this.loading = false
    },

    toggleRequiredModal() {
      this.$modal.show('required-modal')
    },

    toggleObjectsModal() {
      this.$modal.show('objects-modal')
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
    async listValidations(query_params = {}) {
      try {
        this.validations.filters = query_params
        this.validations.refresh()
      } catch {
        this.$Alert.alert({
          type: 'error',
          timeout: 2000,
          message: 'There was an error gathering validations',
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

            this.$router.go()
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

    openStageDropDown() {
      this.resource = 'Opportunity'
      this.formType = 'STAGE_GATING'
      this.getStageForms()
      this.stageDropDownOpen = !this.stageDropDownOpen
    },

    async onAddForm() {
      this.selectingStage = !this.selectingStage
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
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
.back-logo {
  position: absolute;
  opacity: 0.06;
  filter: alpha(opacity=50);
  height: 36%;
  margin-left: -2rem;
  margin-top: 10rem;
}
.container {
  margin-left: 12vw;
  margin-top: 4rem;
  color: $base-gray;
  display: flex;
  align-items: center;
  flex-direction: column;
  height: 100%;
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
::v-deep .vm--modal {
  background-color: $panther;
  border-radius: 0.25rem;
}
::v-deep .tn-dropdown__selection-container {
  box-shadow: 0 5px 10px 0 $very-light-gray;
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
  min-height: 50vh;
  width: 30vw;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin-top: 1rem;
  border-radius: 1rem;
  background-color: $white;
  color: $base-gray;
  box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
  &__box {
    &__title {
      text-align: center;

      width: 100%;
    }

    &__content {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      min-height: 20rem;
    }
    &__button {
      @include primary-button();
      background-color: $dark-green;
      color: $white;
      padding: 0.5rem 2rem;
      margin: 1rem;
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
  align-items: flex-start;
  flex-direction: row;
  height: 100%;
}
.small__stage__dropdown {
  padding: 6px 0 14px;
  border-radius: 0.5rem;
  box-shadow: 0 5px 10px 10px rgba(0, 0, 0, 0.5);
  background-color: $white;
  overflow-y: scroll;
}
.stage {
  &__container {
    position: relative;
  }
  &__dropdown {
    min-height: 40vh;
    min-width: 28vw;
    padding: 6px 0 14px;
    border-radius: 0.5rem;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    background-color: $white;
    overflow-y: scroll;

    &__header {
      font-size: 1.25rem;
      padding: 0.5rem;
      text-align: center;
    }
    &__stages {
      &__container {
        display: flex;
        background-color: $dark-green;
        height: 2.5rem;
        padding: 1rem;
        margin: 0.5rem;
        border-radius: 0.33rem;
        font-size: 0.75rem;
        cursor: pointer;
        align-items: center;

        &--selected {
          color: white;
        }
      }
      &__title {
        font-size: 1rem;
        font-family: #{$bold-font-family};
        cursor: pointer;

        padding: 0.2rem;
        margin-bottom: 0.2rem;
        margin-top: 0.5rem;
        width: 100%;
      }
      &__title:hover {
        color: $very-light-gray;
      }
      &__x {
        z-index: 1000;
        font-size: 1rem;
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
