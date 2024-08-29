<template>
  <div>
    <div style="margin: 24px 0" v-if="!headers.length">
      <p>Import your contacts using an Excel or CSV file.</p>
    </div>
    <div style="margin: 24px 0 0 0" v-else>
      <p>Match each ManagrAI field with the corresponding label from your contacts</p>
    </div>
    <div style="margin-top: 32px" class="table-border" v-if="headers.length">
      <div v-for="field in fields" :key="field" class="header">
        <p style="margin: 12px 0 20px 0">{{ formatString(field) }}</p>
        <select v-model="fieldMapping[field]">
          <option value="">{{ formatPlaceholder(field) }}</option>
          <option v-for="header in headers" :key="header" :value="header">
            {{ header }}
          </option>
        </select>
      </div>
    </div>

    <div v-else class="table-border-center">
      <div v-if="!sheets.length" class="file-input-wrapper">
        <label class="file-input-label">
          <input type="file" @change="readColumnNames" class="file-input" />
          <span style="margin-right: 4px" class="secondary-button">
            <img
              v-if="loading"
              style="margin-right: 4px"
              class="invert rotation"
              src="@/assets/images/loading.svg"
              height="14px"
              alt=""
            />
            Upload File
          </span>
        </label>
        <p class="file-name">{{ fileName ? fileName : 'No file selected' }}</p>
      </div>

      <div class="row" v-else>
        <select v-model="selectedSheet">
          <option value="">Select a sheet</option>
          <option v-for="(sheet, i) in sheets" :key="i" :value="sheet">
            {{ sheet.name }}
          </option>
        </select>

        <button
          style="border-radius: 50%; padding: 8px"
          class="primary-button"
          @click="selectSheet"
          :disabled="!selectedSheet"
        >
          <img src="@/assets/images/arrow-right.svg" height="14px" alt="" />
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { Comms } from '@/services/comms'

export default {
  data() {
    return {
      sheets: [],
      selectedSheet: '',
      headers: [],
      previewData: [],
      columnMappings: {},
      fieldMapping: {},
      fileName: '',
      loading: false,
      selectedFile: null,
      fieldsmapped: false,
      fields: ['publication', 'first_name', 'last_name', 'email'],
    }
  },
  watch: {
    fieldMapping: {
      handler(newMappings) {
        const requiredFields = ['publication', 'first_name', 'last_name', 'email']
        const allFieldsHaveValues = requiredFields.every(
          (field) => newMappings[field] && newMappings[field] !== 'ignore',
        )

        this.fieldsmapped = allFieldsHaveValues

        if (allFieldsHaveValues) {
          this.mappedColumns = newMappings
          this.$emit('fieldsFullyMapped', newMappings, this.selectedFile, this.selectedSheet.name)
        }
      },
      deep: true,
    },
  },
  methods: {
    test() {
      console.log(this.columnMappings)
    },
    formatString(txt) {
      let formattedString

      switch (txt) {
        case 'publication':
          formattedString = 'Publication'
          break
        case 'first_name':
          formattedString = 'First Name'
          break
        case 'last_name':
          formattedString = 'Last Name'
          break
        case 'email':
          formattedString = 'Email'
          break
        default:
          formattedString = ''
          break
      }

      return formattedString
    },
    formatPlaceholder(txt) {
      let formattedString

      switch (txt) {
        case 'publication':
          formattedString = 'Selct publication'
          break
        case 'first_name':
          formattedString = 'Select first name'
          break
        case 'last_name':
          formattedString = 'Select last name'
          break
        case 'email':
          formattedString = 'Select email'
          break
        default:
          formattedString = ''
          break
      }

      return formattedString
    },
    async readColumnNames(event) {
      this.loading = true
      const file = event.target.files[0]
      this.selectedFile = file
      try {
        const res = await Comms.api.readColumnNames(file)
        this.sheets = res.sheets
        console.log(res)

        this.loading = false
      } catch (e) {
        console.log(e)
      }
    },

    selectSheet() {
      console.log(this.selectedSheet)
      this.headers = this.selectedSheet.columns
      this.sheetName = this.selectedSheet.name
      this.$set(this, 'fieldMappings', {})
      this.fields.forEach((field) => {
        this.$set(this.fieldMapping, field, '')
      })
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  border-radius: 16px;

  &:disabled {
    img {
      filter: none;
    }
  }
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
  }
}

.img-container-stay {
  padding: 6px 8px 4px 7px;
  border-radius: 50%;
  background-color: $soft-gray;
  border: 1px solid rgba(0, 0, 0, 0.1);
  margin-left: 12px;

  img {
    margin: 0;
    padding: 0;
  }
}
h3 {
  font-family: $base-font-family;
}
.header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  p {
    font-family: $base-font-family;
  }
  margin-bottom: 5px;
}

p {
  font-size: 16px;
}
.table-border-center {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  height: 250px;
  overflow: scroll;
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.table-border {
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  height: 340px;
  overflow: scroll;
  margin-top: 16px;
  overflow-y: scroll;
  scroll-behavior: smooth;
  // padding: 16px;

  &::-webkit-scrollbar {
    width: 5px;
    height: 0px;
  }
  &::-webkit-scrollbar-thumb {
    background-color: $soft-gray;
    box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
    border-radius: 6px;
  }
}

select {
  width: 200px;
  padding: 8px 12px;
  font-family: $thin-font-family;
  font-size: 14px;
  color: $dark-blue;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
  appearance: none;
  background-image: url('~@/assets/images/dropdown.svg');
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 16px;

  &:hover {
    background-color: $soft-gray;
  }

  &:focus {
    outline: none;
    border-color: $dark-black-blue;
  }
}

.file-input-wrapper {
  display: flex;
  flex-direction: row;
  align-items: center;
  font-family: $thin-font-family;
}

.file-input-label {
  display: inline-flex;
  align-items: center;
  cursor: pointer;
}

.file-input {
  display: none;
}

.secondary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
}

.file-name {
  margin-top: 10px;
  font-size: 14px;
  color: #333333;
  font-weight: 400;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotation {
  animation: rotation 2s infinite linear;
}

.invert {
  filter: invert(40%) !important;
}
.spantext {
  span {
    font-family: $base-font-family;
  }
}
</style>
