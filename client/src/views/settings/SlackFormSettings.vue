<template>
  <div class="container">
    <div :key="i" class="box" v-for="(resource, i) in FORM_RESOURCES">
      <div @click="toggleSelectedFormResource(resource)" class="box__header">
        <span class="box__title">
          {{ resource }}
        </span>
      </div>

      <div :ref="`${resource.toLowerCase()}-content`" class="box__content">
        <div class="box__tab-header">
          <div
            class="box__tab"
            :class="{ 'box__tab--active': selectedTab == 'MEETING_REVIEW' }"
            @click="toggleSelectedTab('MEETING_REVIEW')"
          >
            Meeting Review Form
          </div>
          <div
            class="box__tab"
            :class="{ 'box__tab--active': selectedTab == 'CREATE' }"
            @click="toggleSelectedTab('CREATE')"
          >
            Create {{ resource }} Form
          </div>
          <div
            class="box__tab"
            :class="{ 'box__tab--active': selectedTab == 'UPDATE' }"
            @click="toggleSelectedTab('UPDATE')"
          >
            Update {{ resource }} Form
          </div>
        </div>
        <div class="box__tab-content">
          <template v-if="selectedForm">
            <p>
              <i
                >Required Fields have been pre-filled as part of the form, add or remove additional
                fields</i
              >
              <br />
              <strong>Additional Validations may apply for your Salesforce Resources</strong
              ><button @click="showValidations = !showValidations">Click Here</button
              ><strong>to view them</strong>
            </p>

            <CustomSlackForm
              :show-validations="showValidations"
              :customForm="selectedForm"
              :formType="selectedTab"
              :resource="resource"
              v-on:update:selectedForm="updateForm($event)"
            />
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CustomSlackForm from '@/views/settings/CustomSlackForm'
import { mapState } from 'vuex'
import SlackOAuth, { salesforceFields } from '@/services/slack'
import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'SlackFormSettings',
  components: { CustomSlackForm },
  data() {
    return {
      allForms: [],
      formsByType: [],
      isLoading: false,
      selectedTab: null,
      resource: null,
      selectedForm: null,
      showValidations: false,
      ...FORM_CONSTS,
    }
  },
  watch: {},
  async created() {
    try {
      this.allForms = await SlackOAuth.api.getOrgCustomForm()

      //

      //this.toggleSelectedTab('MEETING_REVIEW')
    } catch (error) {
      console.log(error)
    }
  },
  computed: {
    ...mapState(['user']),
  },
  methods: {
    toggleSelectedFormResource(resource) {
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
      if (this.resource == this.CONTACT) {
        this.toggleSelectedTab(this.CREATE)
      } else {
        this.toggleSelectedTab(this.MEETING_REVIEW)
      }
    },
    toggleSelectedTab(tab) {
      this.selectedTab = tab
      let form = this.formsByType.find(f => f.formType == tab)

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

.box__header {
  &:hover {
    cursor: pointer;
  }
}
.box__content {
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
</style>
