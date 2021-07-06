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
            <div class="modal-container__box__title">Select a stage</div>
          </div>
          <div class="modal-container__box__content">
            <div class="box__content-select">
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

          <div class="modal-container__box__footer">
            <div style="display: flex; align-items: center; flex-direction: column">
              <span class="user-message" v-if="!stages.length">
                <small>Can't see your stages?</small>
              </span>
              <span v-else class="user-message">
                <small>Recently updated your stages?</small>
              </span>
              <PulseLoadingSpinnerButton
                @click="() => refreshFormStages()"
                :loading="false"
                class="primary-button"
                text="Refresh"
              />
            </div>
            <div>
              <button
                class="modal-container__box__button"
                @click="
                  () => {
                    $modal.hide('add-stage-modal'),
                      addForm(this.selectedStage),
                      toggleSelectedTab(`.${this.selectedStage}`)
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

    <modal name="objects-modal" heading="Select a Stage">
      <div class="required__container">
        <img class="tooltip image" src="@/assets/images/toolTip.png" @click="toggleObjectsModal" />
        <div class="required__title">Forms</div>
        <div class="required__instructions">
          <strong>Create:</strong>
          This form is triggered when you run the slack command, "managr-create".
          <br />
          <strong>Update (Command):</strong>
          This form is triggered when you run the slack command, "managr-update".
          <br />
          <strong>Update (zoom):</strong>
          This form is triggered immediately after a zoom meeting ends.
          <br />
          <strong>Stage Specific:</strong>
          Added fields that are needed to progress into a new stage / pass validation rules
        </div>
      </div>
    </modal>

    <div class="header__container">
      <h3 class="header__title">Slack form builder</h3>
      <div class="header__list">
        <div class="header__list__item">
          <h3 class="muted">Map your Salesforce fields to Managr</h3>
        </div>
      </div>
    </div>

    <div class="main__content">
      <div class="box-updated">
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
        <div class="row">
          <DropDownSearch
            :items.sync="SOBJECTS_LIST"
            v-model="resource"
            displayKey="key"
            valueKey="value"
            nullDisplay="Select Salesforce Object"
          />
          <div v-if="resource">
            <button @click="selectForm(resource, CREATE)" class="buttons__">Create</button>
            <button @click="selectForm(resource, UPDATE)" class="buttons__">
              Update (Command)
            </button>
            <button
              @click="selectForm(resource, MEETING_REVIEW)"
              v-if="resource == 'Opportunity' || resource == 'Account'"
              class="buttons__"
            >
              Update (Zoom)
            </button>
            <button
              @click="selectForm(resource, STAGE_GATING)"
              v-if="resource == 'Opportunity'"
              class="buttons__"
            >
              Stage Specific
            </button>
            <img
              style="height: 1.6rem; padding-left: 0.5rem; padding-bottom: 0.5rem; cursor: pointer"
              src="@/assets/images/toolTip.png"
              @click.prevent.stop="toggleObjectsModal"
            />
          </div>
        </div>

        <div class="box__tab-content">
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
              />
            </div>
          </template>
        </div>
      </div>
    </div>

    <div class="tip-continue">
      <div class="row">
        <strong>Hint: </strong>
        <p class="hint">Start with Opportunity then Contact objects, as they are used most.</p>
      </div>
      <button class="primary-button">
        <router-link :to="{ name: 'CreateNew' }">Continue to Smart Alerts </router-link>
      </button>
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
import DropDownSearch from '@/components/DropDownSearch'
import { SOBJECTS_LIST } from '@/services/salesforce'
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
      stageDropDownOpen: false,
      isVisible: false,
      validations: CollectionManager.create({
        ModelClass: SObjectValidation,
        pagination: Pagination.create({ size: 2 }),
      }),
    }
  },
  watch: {
    selectedFormType: {
      immediate: true,
      async handler(val, prev) {},
    },
  },
  async created() {
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      // this.allFields = await this.listFields()
      // await this.listPicklists({
      //   salesforceObject: this.Opportunity,
      //   picklistFor: 'StageName',
      // })
    } catch (error) {
      console.log(error)
    }
  },
  computed: {
    ...mapState(['user']),
    selectedFormType() {
      return this.selectedForm ? this.selectedForm.formType : null
    },
    formTabHeaders() {
      if (this.resource == this.CONTACT) {
        return this.FORM_TYPES.filter(t => t != this.MEETING_REVIEW)
      } else if (this.resource == this.OPPORTUNITY) {
        return [...this.FORM_TYPES, this.STAGE_GATING]
      }
      return this.FORM_TYPES
    },
    allFormsByType() {
      // this getter gets all forms byType existing and new (new forms arent appended until they are created)
      return [...this.formsByType, ...this.newForms]
    },

    currentFormStages() {
      // users can only create one form for the stage
      if (this.resource == this.OPPORTUNITY) {
        return this.allFormsByType.filter(f => f.formType == this.STAGE_GATING).map(f => f.stage)
      }
      return []
    },
    formStages() {
      // users can only create one form for the stage orderd by stage
      let forms = []
      if (this.resource == this.OPPORTUNITY) {
        this.stages.forEach(s => {
          this.allFormsByType
            .filter(f => f.formType == this.STAGE_GATING)
            .forEach(sf => {
              if (sf.stage == s.value) {
                forms.push(sf)
              }
            })
        })
      }
      return forms
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

    async selectForm(resource, formType) {
      this.selectedForm = this.allForms.find(f => f.resource == resource && f.formType == formType)
      this.formType = formType
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

    async listPicklists(query_params = {}) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)

        this.stages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },

    async deleteForm(form) {
      const forms = this.allFormsByType

      if (form.id.length) {
        const id = form.id

        SlackOAuth.api
          .delete(id)
          .then(async res => {
            this.$Alert.alert({
              type: 'success',

              message: 'Form deleted successfully',

              timeout: 2000,
            })

            const forms = this.formsByType.filter(f => {
              return f.id !== form.id
            })
            this.formsByType = forms
          })

          .catch(e => {
            this.$Alert.alert({
              type: 'error',

              message: 'There was an error, please try again',

              timeout: 2000,
            })
          })

          .finally(() => {})
      } else {
        const forms = this.newForms.filter(f => {
          return f.id !== form.id
        })
        this.newForms = forms
      }
    },

    openStageDropDown() {
      this.stageDropDownOpen = !this.stageDropDownOpen
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

      if (this.currentFormStages.includes(stage)) {
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
        let fields = curr.fieldsRef.filter(f => !acc.map(af => af.id).includes(f.id))
        acc = [...acc, ...fields]
        return acc
      }, [])
      this.newForms = [...this.newForms, newForm]
    },
    async toggleSelectedFormResource(resource) {
      this.isVisible = !this.isVisible
      await this.listValidations({ salesforceObject: this.resource })
      /** This Toggle Method handles the classes note the setTimeout must be set to match the animation time */
      if (this.resource && resource) {
        if (this.resource == resource) {
          let classList = this.$refs[`${resource.toLowerCase()}-content`][0].classList
          if (classList.contains('box__content--expanded')) {
            classList.toggle('box__content--closed')
            classList.toggle('box__content--expanded')
            setTimeout(() => {
              classList.toggle('box__content--closed')
            }, 500)
          } else if (classList.contains('box__content--closed')) {
            classList.toggle('box__content--expanded')
            classList.toggle('box__content--closed')
          } else {
            classList.toggle('box__content--expanded')
          }
        } else {
          let prev = this.resource
          this.resource = resource
          this.formsByType = this.allForms.filter(f => f['resource'] == this.resource)

          let prevClassList = this.$refs[`${prev.toLowerCase()}-content`][0].classList
          let classList = this.$refs[`${this.resource.toLowerCase()}-content`][0].classList
          if (prevClassList.contains('box__content--expanded')) {
            prevClassList.toggle('box__content--closed')
            prevClassList.toggle('box__content--expanded')
            setTimeout(() => {
              prevClassList.toggle('box__content--closed')
            }, 500)
          }
          classList.toggle('box__content--expanded')
        }
      } else {
        this.resource = resource
        this.formsByType = this.allForms.filter(f => f['resource'] == this.resource)
        let classList = this.$refs[`${this.resource.toLowerCase()}-content`][0].classList
        classList.toggle('box__content--expanded')
      }

      let f = this.allFormsByType[0]
      this.toggleSelectedTab(`${f.id}.${f.stage}`)
    },
    toggleSelectedTab(tab) {
      this.selectedTab = tab
      let [id, stage] = tab.split('.')

      let form = this.allFormsByType.find(f => f.id == id && f.stage == stage)

      if (form && typeof form != undefined) {
        this.selectedForm = form
      } else this.selectedForm = null
    },
    updateForm(event) {
      this.selectedForm = event
      let index = this.formsByType.findIndex(f => f.id == this.selectedForm.id)

      if (~index) {
        this.formsByType[index] = this.selectedForm
        this.formsByType = [...this.formsByType]
      }
      this.selectedTab = `${event.id}.${event.tage}`
    },
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
  padding: 0 4rem;
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
.modal-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-top: 1rem;
  border-radius: 10px;

  &__box {
    &__title {
      text-align: center;
      margin: 2rem 0;

      width: 100%;
    }

    &__content {
      display: flex;

      justify-content: center;
      min-height: 35rem;
    }
    &__button {
      @include primary-button();
      margin-top: 1rem;
      width: 10rem;
    }
    &__footer {
      display: flex;
      padding: 0rem 1rem;

      justify-content: space-between;
      border-top: 2px solid $dark-green;
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
.stage {
  &__container {
    position: relative;
  }
  &__dropdown {
    width: 15rem;

    margin: 18px 113px 49px 108px;
    padding: 6px 0 14px;
    border-radius: 3px;
    box-shadow: 0 5px 10px 0 rgba(0, 0, 0, 0.2);
    background-color: #f4f5f6;
    position: absolute;
    right: -7rem;

    z-index: 100;

    &__header {
      font-size: 0.75rem;
      padding: 0.5rem;
      border-bottom: solid 0.5px #9e9ea6;
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
          color: white !important;
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
  margin: 2rem 0rem;
}

.required {
  &__container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  &__title {
    font-family: #{$bold-font-family};
    border-bottom: 2px solid #2f9e54;
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
  margin-bottom: 1em;
}
button {
  margin-top: 1em;
}
.buttons__ {
  height: 3rem;
  width: 11rem;
  text-align: center;
  border-radius: 0.75rem;
  border: 2px solid #199e54;
  color: #199e54;
  background-color: white;
  font-weight: bolder;
  box-shadow: -0.5px 0.3px 0.5px 0.5px grey;
  margin-right: 1.5rem;
}
.buttons__:hover {
  background-color: #199e54;
  color: white;
  cursor: pointer;
}
.primary-button:hover {
  transform: scale(1.05);
}
</style>
