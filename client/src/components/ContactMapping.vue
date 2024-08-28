<template>
  <div>
    <div>
      <p>
        Import your contact list and link columns to fields like publication, name, and email. (MIKE
        WILL FIX)
      </p>
    </div>
    <div class="table-border" v-if="headers.length">
      <table>
        <thead>
          <tr>
            <th v-for="(header, index) in headers" :key="index">
              <select v-model="columnMappings[header]" :key="header">
                <option value="">Select a field</option>
                <option value="email">Email</option>
                <option value="first_name">First Name</option>
                <option value="last_name">Last Name</option>
                <option value="publication">Publication</option>
                <option value="ignore">Ignore</option>
              </select>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in previewData" :key="rowIndex">
            <td v-for="(cell, cellIndex) in row" :key="cellIndex">
              <div class="set-width">
                {{ cell }}
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-else class="table-border-center">
      <div class="file-input-wrapper">
        <label class="file-input-label">
          <input type="file" @change="handleFileUpload" class="file-input" />
          <span style="margin-right: 4px" class="secondary-button">Upload File</span>
        </label>
        <p class="file-name">{{ fileName ? fileName : 'No file selected' }}</p>
      </div>
    </div>
    <button v-if="previewData" @click="confirmMapping">Confirm Mapping</button>
  </div>
</template>

<script>
export default {
  data() {
    return {
      headers: [],
      previewData: [],
      columnMappings: {},
      fileName: '',
    }
  },
  methods: {
    handleFileUpload(event) {
      const file = event.target.files[0]
      this.fileName = file.name
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          try {
            const text = e.target.result // Read the file content as text
            this.processFile(text)
          } catch (error) {
            console.error('Error reading the file:', error)
          }
        }
        reader.readAsText(file) // Read the file as text
      }
    },
    processFile(text) {
      if (!text || text.trim().length === 0) {
        console.error('Empty or invalid file data.')
        return
      }

      // Split the text by new lines to get rows
      const rows = text.split('\n').filter((row) => row.trim() !== '')

      if (rows.length === 0) {
        console.error('No valid data rows found in the file.')
        return
      }

      // Split each row by tabs to get cells
      const sheet = rows.map((row) => row.split('\t'))

      // Extract headers (first row)
      this.headers = sheet[0] || []

      // Extract data (next rows) and limit preview to first 5 rows
      this.previewData = sheet.slice(1, 6)

      // Initialize column mappings with empty values
      this.headers.forEach((header) => {
        this.$set(this.columnMappings, header, '')
      })
    },
    confirmMapping() {
      const mappedColumns = {}
      Object.keys(this.columnMappings).forEach((header) => {
        if (this.columnMappings[header] && this.columnMappings[header] !== 'ignore') {
          mappedColumns[this.columnMappings[header]] = header
        }
      })

      // Emit the mappings to the parent component
      this.$emit('mappingConfirmed', mappedColumns)
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

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
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 6px;
  height: 340px;
  overflow: scroll;
  margin-top: 16px;
}

table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;

  th,
  td {
    padding: 12px;
    font-size: 14px;
    text-align: left;
    position: relative;
  }

  thead {
    position: sticky;
    top: 0;
    z-index: 8;
  }

  th {
    background-color: $off-white;
    border-bottom: 0.5px solid rgba(0, 0, 0, 0.1);
    color: $dark-blue;
    cursor: pointer;
  }

  td {
    z-index: 1;
    background-color: white;
    overflow: hidden;
    width: 10vw;
    height: 50px;
  }
}

.set-width {
  width: 10vw;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gray-bg {
  background-color: $off-white !important;
}

select {
  width: 100%;
  padding: 8px 12px;
  font-family: $thin-font-family;
  font-size: 14px;
  color: $dark-blue;
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  transition: background-color 0.3s ease, border-color 0.3s ease;
  appearance: none; // Hide the default arrow
  background-image: url('~@/assets/images/dropdown.svg'); // Replace with the actual path to your custom image
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
  //   'Inter', sans-serif; You can use a clean, modern font like Inter
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
</style>
