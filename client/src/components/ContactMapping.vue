<template>
  <div>
    <div v-if="!headers.length">
      <p>Import your contacts using an Excel file.</p>
    </div>
    <div v-else>
      <p @click="test" class="spantext">
        Select the columns that contain the <span>Publication</span>,
        <span>Journalist's first</span> and <span>last name</span>, and <span>Email address</span>.
        Ignore all other fields.
      </p>
    </div>
    <div class="table-border" v-if="headers.length">
      <div v-for="(header, i) in headers" :key="i" class="header">
        <p>{{ header }}</p>
        <select v-model="columnMappings[header]">
          <option value="">Select a field</option>
          <option value="email">Email</option>
          <option value="first_name">First Name</option>
          <option value="last_name">Last Name</option>
          <option value="publication">Publication</option>
        </select>
      </div>
    </div>
    <div v-else class="table-border-center">
      <div class="file-input-wrapper">
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
    </div>
  </div>
</template>

<script>
import { Comms } from '@/services/comms'

export default {
  data() {
    return {
      headers: [],
      previewData: [],
      columnMappings: {},
      fileName: '',
      loading: false,
      selectedFile: null,
      fieldsmapped: false,
    }
  },
  watch: {
    columnMappings: {
      handler(newMappings) {
        const requiredFields = ['publication', 'first_name', 'last_name', 'email']
        const allMapped = requiredFields.every((field) =>
          Object.values(newMappings).includes(field),
        )
        console.log(allMapped)

        this.fieldsmapped = allMapped
      },
      deep: true,
    },
    fieldsmapped() {
      const mappedColumns = {}
      Object.keys(this.columnMappings).forEach((header) => {
        if (this.columnMappings[header] && this.columnMappings[header] !== 'ignore') {
          mappedColumns[this.columnMappings[header]] = header
        }
      })
      this.$emit('fieldsFullyMapped', mappedColumns, this.selectedFile)
    },
  },
  methods: {
    test() {
      console.log(this.columnMappings)
    },
    async readColumnNames(event) {
      this.loading = true
      const file = event.target.files[0]
      this.selectedFile = file
      try {
        const res = await Comms.api.readColumnNames(file)
        this.headers = res.columns

        // Initialize columnMappings with reactive properties
        this.$set(this, 'columnMappings', {}) // Ensure columnMappings is reactive
        this.headers.forEach((header) => {
          this.$set(this.columnMappings, header, '')
        })

        this.loading = false
      } catch (e) {
        console.log(e)
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.header {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  padding-right: 12px;
  p {
    font-family: $base-font-family;
  }
}

p {
  font-size: 14px;
}
.table-border-center {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  height: 300px;
  overflow: scroll;
  margin-top: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.table-border {
  border-radius: 6px;
  height: 340px;
  overflow: scroll;
  margin-top: 16px;
  overflow-y: scroll;
  scroll-behavior: smooth;

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
