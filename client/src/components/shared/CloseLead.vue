<template>
  <div class="close-lead">
    <h1><span class="emoji">🎉</span>Congrats on the Deal! - Go Ring the Bell!</h1>
    <!-- client side validations -->
    <div class="errors" v-if="isFormValid !== null && !isFormValid">
      No field may be blank.
    </div>
    <!-- form -->
    <form @submit.prevent="closeLead">
      <div class="form-field">
        <label>Final Contract Amount</label>
        <div class="flex-container bordered">
          <img class="icon" alt="icon" src="@/assets/images/claimed.svg" />
          <input v-model="amount" type="number" placeholder="Final Dollar Amount" />
        </div>
      </div>
      <div class="form-field">
        <label>Final Contract</label>
        <div class="flex-container">
          <input ref="upload" type="file" :style="{ display: 'none' }" @change="onFileChosen" />
          <button type="button" class="upload-button" @click.prevent="chooseFile">
            <img class="icon" alt="icon" src="@/assets/images/add.svg" />
            Choose File
          </button>
          <span v-if="file" class="file-name">{{ file.name }}</span>
        </div>
      </div>
      <div class="form-field">
        <label>Close Note</label>
        <textarea v-model="note" class="bordered" placeholder="Input note" />
      </div>
      <div class="cta-container">
        <button type="submit" class="cta">Close Opportunity</button>
      </div>
    </form>
  </div>
</template>

<script>
import File from '@/services/files'
import Lead from '@/services/leads'

export default {
  name: 'CloseLead',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      amount: '',
      file: null,
      note: '',
      errors: {},
      isFormValid: null,
      success: null,
    }
  },
  methods: {
    chooseFile() {
      this.$refs.upload.click()
    },
    onFileChosen(e) {
      this.file = e.target.files[0]
    },
    closeLead() {
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

      // proceed to close the lead, first uploading the contract
      File.api
        .create(this.file, this.lead.id)
        .then(response => {
          return Lead.api.close(this.lead.id, this.amount, response.data.id)
        })
        .then(() => {
          this.lead.status = Lead.CLOSED
          if (this.lead.forecastRef) {
            this.lead.forecastRef.forecast = Lead.CLOSED
          }
          this.lead.closingAmount = parseFloat(this.amount)
          this.$parent.$emit('closed-lead')
          this.$parent.$emit('close-modal')
          this.$Alert.alert({
            type: 'success',
            timeout: 3000,
            message: 'Success! Opportunity closed!',
          })
        })
    },
    clientSideValidations() {
      let formErrors = {
        amountIsBlank: this.amountIsBlank,
        noteIsBlank: this.noteIsBlank,
        noFileChosen: this.noFileChosen,
      }
      let isFormValid = !this.amountIsBlank && !this.noteIsBlank && !this.noFileChosen

      return [isFormValid, formErrors]
    },
  },
  computed: {
    amountIsBlank() {
      return !this.amount.length
    },
    noteIsBlank() {
      return !this.note.length
    },
    noFileChosen() {
      return this.file === null
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/mixins/inputs';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';

.close-lead {
  @include base-font-styles();
  display: flex;
  flex-flow: column;
  align-items: center;
}

h1 {
  width: 96%;
  display: flex;
  flex-flow: row;
  align-items: center;
}

.emoji {
  margin-right: 1rem;
}

.errors {
  color: $coral;
}

form {
  margin-top: 2rem;
  width: 50%;
  box-sizing: border-box;
  display: flex;
  flex-flow: column;
}

.form-field {
  display: flex;
  flex-flow: column;
  margin-top: 1rem;
}

label {
  font-size: 1.2rem;
}

textarea {
  @include input-field();
  background-color: $white;
  resize: none;
  height: 6rem;
  margin-top: 0.5rem;

  &:focus {
    box-shadow: 0 0 0 rgba($color: $dark-green, $alpha: 0.5);
  }
}

.bordered {
  @include standard-border();
}

.flex-container {
  margin-top: 0.5rem;
  display: flex;
  flex-flow: row;
  align-items: center;
  background-color: $white;
  width: auto;

  input {
    @include input-field();
    flex-grow: 1;
    background-color: $white;
    height: 2rem;
    width: 20rem;

    &:focus {
      box-shadow: 0 0 0 rgba($color: $dark-green, $alpha: 0.5);
    }
  }
}

.icon {
  margin-left: 1rem;
  margin-right: 0.5rem;
}

.upload-button {
  @include secondary-button();
  margin-right: 2rem;
  font-size: 0.8rem;

  .icon {
    height: 1rem;
    margin-left: 0;
    margin-right: 0.5rem;
  }
}

.file-name {
  font-weight: bold;
  opacity: 0.4;
}

.cta-container {
  margin-top: 2rem;
  display: flex;
  flex-flow: row;
}

.cta {
  @include primary-button();
  margin-left: auto;
}
</style>
