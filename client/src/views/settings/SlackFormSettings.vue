<template>
  <div class="container">
    <modal name="add-stage-modal" heading="Select a Stage" height="500" adaptive>
      <div class="modal-container">
        <div v-if="!loadingStages" class="modal-container__box">
          <div class="modal-container__box__header">
            <div class="modal-container__box__title">Select a stage</div>
          </div>
          <div class="modal-container__box__content">
            <div class="box__content-select">
              <DropDownSearch
                :items="stages"
                v-model="selectedStage"
                displayKey="label"
                valueKey="value"
                nullDisplay="Select a Stage"
                searchable
              />
            </div>
          </div>

          <div class="box__footer">
            <button
              @click="
                () => {
                  $modal.hide('add-stage-modal'),
                    addForm(this.selectedStage),
                    toggleSelectedTab(`.${this.selectedStage}`)
                }
              "
            >Select</button>
          </div>
        </div>
        <div v-else>LOADING</div>
      </div>
    </modal>

    <div class="header__container">
      <h3 class="header__title">Customize your Slack form</h3>
      <div class="header__list">
        <div
          class="header__list__item"
        >1. Customize your Slack forms by picking from the fields on the left. Note required “Managr” fields have been preselected</div>
        <div class="header__list__item">2. Please make sure to fill out all the tabs for all Objects</div>
        <div
          class="header__list__item"
        >3. If your company has Validation rules, like “Stage Gating” fill out that tab as well by selecting each Stage that is gated</div>
        <div
          class="header__list__item"
        >4. Make sure to double check that all your required fields are on the form</div>
      </div>
    </div>
    <div :key="i" class="box-updated" v-for="(resource, i) in FORM_RESOURCES">
      <template v-if="allForms && allForms.length">
        <div @click="toggleSelectedFormResource(resource)" class="box-updated__header">
          <span class="box-updated__title">{{ resource }}</span>
        </div>

        <div :ref="`${resource.toLowerCase()}-content`" class="box-updated__content">
          <div class="box-updated__tab-header">
            <div
              :key="i"
              v-for="(k, i) in allFormsByType"
              class="box-updated__tab"
              :class="{ 'box-updated__tab--active': selectedTab == `${k.id}.${k.stage}` }"
              @click="toggleSelectedTab(`${k.id}.${k.stage}`)"
            >{{ k.formType | snakeCaseToTextFilter }} {{ k.stage }}</div>

            <div
              class="box-updated__tab"
              @click="onAddForm"
              v-if="resource == OPPORTUNITY"
            >Stage Specific</div>
          </div>

          <div class="box__tab-content">
            <template v-if="selectedForm">
              <p>
                <i>
                  Required Fields have been pre-filled as part of the form, add or remove
                  additional fields
                </i>
                <br />
                <strong>Additional Validations may apply for your Salesforce Resources</strong>
                <PulseLoadingSpinnerButton
                  @click="showValidations = !showValidations"
                  class="primary-button"
                  text="Click Here"
                  :loading="false"
                />
                <strong>to view them</strong>
              </p>

              <CustomSlackForm
                :fields="selectedFormFields"
                :show-validations="showValidations"
                :customForm="selectedForm"
                :formType="selectedTab"
                :resource="resource"
                v-on:update:selectedForm="updateForm($event)"
              />
            </template>
          </div>
        </div>
      </template>
      <template v-else>We are currently generating your forms please check back in a few minutes</template>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import CustomSlackForm from '@/views/settings/CustomSlackForm'
import { mapState } from 'vuex'
import SlackOAuth, { salesforceFields } from '@/services/slack'
import { SObjectField, SObjectValidation, SObjectPicklist } from '@/services/salesforce'
import DropDownSearch from '@/components/DropDownSearch'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'SlackFormSettings',
  components: { CustomSlackForm, PulseLoadingSpinnerButton, DropDownSearch },
  data() {
    return {
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
      ...FORM_CONSTS,
    }
  },
  watch: {
    selectedFormType: {
      immediate: true,
      async handler(val, prev) {
        console.log(val)
        if (val && val != prev && this.resource) {
          let fieldParam = {}
          if (val == this.CREATE) {
            fieldParam['createable'] = true
          } else {
            fieldParam['updateable'] = true
          }
          try {
            this.selectedFormFields = await this.listFields({
              salesforceObject: this.resource,
              ...fieldParam,
            })
          } catch (e) {
            console.log(e)
          }
        }
      },
    },
  },
  async created() {
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()
      this.allFields = await this.listFields()
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
  },
  methods: {
    async listFields(query_params = {}) {
      try {
        const res = await SObjectField.api.listFields(query_params)
        return res
      } catch (e) {
        console.log(e)
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
      this.newForms = [
        ...this.newForms,
        SlackOAuth.customSlackForm.create({
          resource: this.OPPORTUNITY,
          formType: this.STAGE_GATING,
          stage: stage,
          fields: [],
          fieldsRef: [],
        }),
      ]
    },
    async toggleSelectedFormResource(resource) {
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

.box-updated__header {
  &:hover {
    cursor: pointer;
    background-color: #f4f5f6;
  }
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
}
.modal-container {
  &__box {
    @include box--bordered;
  }
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
  }
  &__list {
    display: flex;
    flex-direction: column;
    text-align: center;
    margin-bottom: 2rem;

    &__item {
      font-size: 14px;
    }
  }
}
</style>
