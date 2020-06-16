<template>
  <div class="flexbox-container">
    <div class="flexbox-container__column">
      <div class="form">
        <div class="form__element">
          <div class="form__element-header">Title</div>
          <input v-model="title" type="text" class="form__input" />
          <div
            class="form__element-error"
            v-if="isFormValid !== null && !isFormValid && errors.titleIsBlank"
          >
            Must include a Title.
          </div>
        </div>
        <div class="form__element">
          <div class="form__element-header">Description</div>
          <textarea v-model="description" class="form__textarea" />
          <div
            class="form__element-error"
            v-if="isFormValid !== null && !isFormValid && errors.descriptionIsBlank"
          >
            Must include a Description.
          </div>
        </div>
      </div>
      <div class="form__element">
        <div class="form__element-header">Date</div>
        <input v-model="date" type="datetime-local" class="form__input" />
        <div
          class="form__element-error"
          v-if="isFormValid !== null && !isFormValid && errors.dateNotSelected"
        >
          Must select a date.
        </div>
      </div>
      <div class="form__element">
        <button class="form__button" @click.prevent="onBulkLogging">Save</button>
      </div>
    </div>
  </div>
</template>

<script>
import Note from '@/services/notes'

export default {
  name: 'BulkNoteAction',
  props: {
    leads: {
      required: true,
      type: Array,
    },
  },
  data() {
    return {
      title: '',
      description: '',
      date: null,
      isFormValid: null,
      errors: {},
    }
  },
  methods: {
    onBulkLogging() {
      // reset component data when submission begins, in case of prior request
      this.isFormValid = null
      this.success = null
      this.errors = {}

      // check form data for this request
      let validationResults = this.clientSideValidations()
      this.isFormValid = validationResults[0]
      this.errors = validationResults[1]
      if (!this.isFormValid) {
        return
      }

      let leads = this.leads.map(l => l.id)
      let data = {
        note: {
          title: this.title,
          content: this.description,
        },
        created_for: leads,
      }
      Note.api.create(data).then(() => {
        this.$Alert.alert({
          type: 'success',
          timeout: 4000,
          message: 'Notes logged for selected leads!',
        })
        this.$parent.$emit('bulk-success')
      })
    },
    clientSideValidations() {
      let formErrors = {
        titleIsBlank: this.titleIsBlank,
        descriptionIsBlank: this.descriptionIsBlank,
        dateNotSelected: this.dateNotSelected,
      }
      let isFormValid = !this.titleIsBlank && !this.descriptionIsBlank && !this.dateNotSelected

      return [isFormValid, formErrors]
    },
  },
  computed: {
    titleIsBlank() {
      return !this.title.length
    },
    descriptionIsBlank() {
      return !this.description.length
    },
    dateNotSelected() {
      return !this.date
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/forms';
@import '@/styles/mixins/inputs';
</style>
