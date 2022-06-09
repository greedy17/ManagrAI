<template>
  <div class="slack-form-builder">
    <div>
      <div>
        <template v-if="showValidations">
          <template v-if="sfValidations.length">
            <ul :key="val.id" v-for="val in sfValidations">
              <li>
                <strong>Title:</strong>
                {{ val.description }}
                <strong>Message:</strong>
                {{ val.message }}
              </li>
            </ul>
          </template>
          <template v-else>{{ resource }} does not appear to have any custom validations</template>
        </template>
      </div>
    </div>
    <!-- <p @click="test">test</p> -->
    <div class="opportunity__row">
      <div :class="formType !== 'STAGE_GATING' ? 'collection_fields' : 'stage_fields'">
        <div v-if="formType === 'STAGE_GATING'">
          <p class="section-title">Add Stage Specific Fields</p>
        </div>
        <div>
          <div v-if="formType === 'STAGE_GATING'">
            <div class="center">
              <button
                v-if="!addingFields"
                @click="
                  () => {
                    addingFields = !addingFields
                  }
                "
                class="default_button"
              >
                Add Fields
                <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
              </button>
            </div>
          </div>

          <div v-if="resource === 'OpportunityLineItem'">
            <div v-if="!addedFieldNames.includes('PricebookEntryId')" class="centered">
              <p style="margin-left: 0.5rem">
                PricebookEntry <span style="color: #fa646a">*</span>
              </p>

              <Multiselect
                placeholder="Select Pricebook field"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
                :loading="dropdownLoading"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>

                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Pricebook field
                  </p>
                </template>
              </Multiselect>
            </div>

            <div v-if="!addedFieldNames.includes('Quantity')" class="centered">
              <p style="margin-left: 0.5rem">Quantity <span style="color: #fa646a">*</span></p>

              <Multiselect
                placeholder="Select Quantity field"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Select Quantity field
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>

        <div v-if="resource === 'Contact'">
          <p class="section-title">Select required form fields:</p>
          <div v-if="formType === 'CREATE'">
            <div v-if="!addedFieldNames.includes('LastName')" class="centered">
              <p style="margin-left: 0.5rem">Last Name <span style="color: #fa646a">*</span></p>

              <Multiselect
                placeholder="Search for 'Last Name'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Last Name'
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>

        <div v-if="resource === 'Lead'">
          <p class="section-title">Select required form fields:</p>
          <div v-if="formType === 'CREATE'">
            <div v-if="!addedFieldNames.includes('LastName')" class="centered">
              <p style="margin-left: 0.5rem">Last Name<span style="color: #fa646a">*</span></p>
              <Multiselect
                placeholder="Search for 'Last Name'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Last Name'
                  </p>
                </template>
              </Multiselect>
            </div>
            <div v-if="!addedFieldNames.includes('Company')" class="centered">
              <p style="margin-left: 0.5rem">Company<span style="color: #fa646a">*</span></p>

              <Multiselect
                placeholder="Search for 'Company'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Company'
                  </p>
                </template>
              </Multiselect>
            </div>
            <div v-if="!addedFieldNames.includes('Status')" class="centered">
              <p style="margin-left: 0.5rem">Status<span style="color: #fa646a">*</span></p>

              <Multiselect
                placeholder="Search for 'Status'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Status'
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>

        <div v-if="resource === 'Account'">
          <p class="section-title">Select required form fields:</p>
          <div v-if="formType === 'CREATE'">
            <div v-if="!addedFieldNames.includes('Name')" class="centered">
              <p style="margin-left: 0.5rem">Account Name <span style="color: #fa646a">*</span></p>

              <Multiselect
                placeholder="Search for Account"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 20vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Account'
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>

        <div v-if="resource === 'Opportunity' && formType !== 'STAGE_GATING'">
          <p class="section-title">Select required form fields:</p>
          <div v-if="!addedFieldLabels.includes('Name')" class="centered">
            <p style="margin-left: 0.5rem">Name: <span style="color: #fa646a">*</span></p>
            <Multiselect
              placeholder="Search for 'Name'"
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              style="width: 20vw"
              selectLabel="Enter"
              track-by="apiName"
              label="referenceDisplayLabel"
              :loading="dropdownLoading"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Search for 'Name'
                </p>
              </template>
            </Multiselect>
          </div>

          <div v-if="!addedFieldNames.includes('StageName')" class="centered">
            <div class="row__">
              <p style="margin-left: 0.5rem">Stage <span style="color: #fa646a">*</span></p>
            </div>
            <Multiselect
              placeholder="Search for 'Stage'"
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              style="width: 20vw"
              selectLabel="Enter"
              track-by="apiName"
              label="referenceDisplayLabel"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Search for 'Stage'
                </p>
              </template>
            </Multiselect>
          </div>

          <div v-if="!addedFieldNames.includes('CloseDate')" class="centered">
            <div class="row__">
              <p style="margin-left: 0.5rem">Close Date <span style="color: #fa646a">*</span></p>
            </div>

            <Multiselect
              placeholder="Search for 'Close Date'"
              :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
              @input="onAddField($event)"
              openDirection="below"
              style="width: 20vw"
              selectLabel="Enter"
              track-by="apiName"
              label="referenceDisplayLabel"
            >
              <template slot="noResult">
                <p class="multi-slot">No results. Try loading more</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">
                  Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                </p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.svg" alt="" />
                  Search for 'Close Date'
                </p>
              </template>
            </Multiselect>
          </div>

          <div
            v-if="!userHasProducts && !addedFieldNames.includes('Amount') && formType !== 'CREATE'"
            class="centered"
          >
            <div class="row__">
              <div style="margin-left: 0.5rem" class="centered">
                <label :class="!productSelected ? 'green' : 'label'">Amount</label>
                <ToggleCheckBox
                  style="margin-left: 0.15rem; margin-right: 0.15rem"
                  :value="productSelected"
                  @input="productSelect"
                  offColor="#41b883"
                  onColor="#41b883"
                />
                <label style="margin-right: 0.15rem" :class="productSelected ? 'green' : 'label'"
                  >Products</label
                >
              </div>
              <p style="font-size: 12px; color: #9b9b9b; margin-left: 0.5rem">(Optional)</p>
            </div>
            <div v-if="!productSelected">
              <Multiselect
                placeholder="Search for 'Amount'"
                :options="
                  formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))
                "
                @input="onAddField($event)"
                openDirection="below"
                style="width: 16vw"
                selectLabel="Enter"
                track-by="apiName"
                label="referenceDisplayLabel"
              >
                <template slot="noResult">
                  <p class="multi-slot">No results. Try loading more</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">
                    Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
                  </p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.svg" alt="" />
                    Search for 'Amount'
                  </p>
                </template>
              </Multiselect>
            </div>

            <div v-if="productSelected">Add products on the next page</div>
          </div>
        </div>

        <p class="section-title">
          Organize your form fields:
          <span style="color: #41b883; font-size: 11px; margin-left: 0.5rem">*drag and drop</span>
        </p>

        <draggable
          style="margin-top: 0.5rem"
          v-model="addedFields"
          group="fields"
          @start="drag = true"
          @end="drag = false"
        >
          <div v-for="field in addedFields" :key="field.id">
            <div :class="unshownIds.includes(field.id) ? 'invisible' : 'centered'">
              <div class="drag-item">
                <img
                  :class="unshownIds.includes(field.id) ? 'invisible' : 'invert2'"
                  src="@/assets/images/drag.svg"
                  id="drag"
                  style="height: 1rem; width: auto; cursor: grab"
                  alt=""
                />
                <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
                  {{ field.referenceDisplayLabel }}
                </p>
              </div>

              <div class="img-border">
                <img
                  src="@/assets/images/trash.png"
                  alt=""
                  id="remove"
                  :class="unshownIds.includes(field.id) ? 'invisible' : 'invert'"
                  @click="
                    () => {
                      onRemoveField(field)
                    }
                  "
                />
              </div>
            </div>
          </div>
        </draggable>

        <div
          v-if="resource === 'Opportunity'"
          style="display: flex; align-items: center; justify-content: center"
        >
          <button
            v-if="requiredOpportunityFields.every((i) => addedFieldNames.includes(i))"
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add more fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>

        <div
          v-else-if="
            resource === 'Contact' &&
            !addingFields &&
            addedFieldNames.includes('LastName') &&
            formType === 'CREATE'
          "
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 0.5rem;
          "
        >
          <button
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add more fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>
        <div
          v-else-if="!addingFields && formType === 'UPDATE' && resource === 'Contact'"
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 0.5rem;
          "
        >
          <button
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>

        <div
          v-else-if="
            resource === 'OpportunityLineItem' &&
            requiredProductFields.every((i) => addedFieldNames.includes(i))
          "
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 0.5rem;
          "
        >
          <button
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add more fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>
        <div
          v-else-if="!addingFields && formType === 'UPDATE' && resource === 'Lead'"
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 0.5rem;
          "
        >
          <button
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add more fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>
        <div
          v-else-if="
            resource === 'Lead' &&
            requiredLeadFields.every((i) => addedFieldNames.includes(i)) &&
            formType === 'CREATE'
          "
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 0.5rem;
          "
        >
          <button
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add more fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>

        <div
          v-else-if="
            resource === 'Account' &&
            !addingFields &&
            addedFieldNames.includes('Name') &&
            formType === 'CREATE'
          "
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 0.5rem;
          "
        >
          <button
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add more fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>

        <div
          v-else-if="!addingFields && formType === 'UPDATE' && resource === 'Account'"
          style="
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
            margin-top: 0.5rem;
          "
        >
          <button
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            class="default_button"
          >
            Add more fields
            <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
          </button>
        </div>

        <div class="example--footer">
          <button
            v-if="
              formType !== 'STAGE_GATING' &&
              resource !== 'OpportunityLineItem' &&
              !(
                (formType === 'UPDATE' && resource === 'Opportunity') ||
                (formType === 'CREATE' && resource === 'Contact')
              )
            "
            style="margin-right: 0.5rem"
            @click="goToOptional"
            class="disabled__"
          >
            Back
          </button>
          <button
            v-if="
              (formType === 'UPDATE' && resource === 'Opportunity') ||
              (formType === 'CREATE' && resource === 'Contact')
            "
            style="margin-right: 0.5rem"
            @click="goBack"
            class="disabled__"
          >
            Back
          </button>
          <button
            v-if="resource === 'OpportunityLineItem'"
            style="margin-right: 0.5rem"
            @click="goToUpdateOpp"
            class="disabled__"
          >
            Back
          </button>
          <div class="row__" v-if="formType === 'STAGE_GATING'">
            <button style="margin-right: 0.5rem" @click="goToValidations" class="disabled__">
              Cancel
            </button>
            <PulseLoadingSpinnerButton
              @click="onSave"
              class="primary-button"
              text="Save"
              :loading="savingForm"
            />
          </div>

          <PulseLoadingSpinnerButton
            v-if="
              resource === 'Opportunity' &&
              !productSelected &&
              !userHasProducts &&
              formType === 'UPDATE'
            "
            @click="onSave"
            class="primary-button"
            :class="
              !requiredOpportunityFields.every((i) => addedFieldNames.includes(i))
                ? 'primary-button'
                : 'primary-button'
            "
            text="Save"
            :loading="savingForm"
            :disabled="!requiredOpportunityFields.every((i) => addedFieldNames.includes(i))"
          />
          <PulseLoadingSpinnerButton
            v-if="resource === 'Opportunity' && !productSelected && formType === 'CREATE'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />

          <div
            v-if="
              resource === 'Opportunity' &&
              (productSelected || userHasProducts) &&
              formType !== 'CREATE' &&
              formType !== 'STAGE_GATING'
            "
          >
            <button
              v-if="requiredOpportunityFields.every((i) => addedFieldNames.includes(i))"
              class="save"
              @click="goToProducts"
            >
              Save + Continue to products
            </button>
            <button v-else class="disabled">Save + Continue to products</button>
          </div>

          <PulseLoadingSpinnerButton
            v-else-if="resource === 'Contact' && formType === 'CREATE'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
            :disabled="!addedFieldNames.includes('LastName')"
          />
          <PulseLoadingSpinnerButton
            v-else-if="resource === 'Contact' && formType === 'UPDATE'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />

          <PulseLoadingSpinnerButton
            v-if="resource === 'OpportunityLineItem'"
            @click="onSave"
            class="primary-button"
            :class="
              !requiredProductFields.every((i) => addedFieldNames.includes(i))
                ? 'primary-button'
                : 'primary-button'
            "
            text="Save"
            :loading="savingForm"
            :disabled="!requiredProductFields.every((i) => addedFieldNames.includes(i))"
          />

          <PulseLoadingSpinnerButton
            v-if="resource === 'Lead' || resource === 'Account'"
            @click="onSave"
            class="primary-button"
            text="Save"
            :loading="savingForm"
          />
        </div>
      </div>

      <div class="recommend" v-if="addingFields">
        <div v-if="formType !== 'STAGE_GATING'" class="recommend__header">
          <h4>Add More Fields</h4>
          <img
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            height="1rem"
            src="@/assets/images/close.svg"
            alt=""
          />
        </div>
        <div class="recommend__header" v-else>
          <h4>Add Fields</h4>
          <img
            @click="
              () => {
                addingFields = !addingFields
              }
            "
            height="1rem"
            src="@/assets/images/close.svg"
            alt=""
          />
        </div>
        <div v-if="formType === 'STAGE_GATING'" class="recommend__body">
          <Multiselect
            placeholder="Search for Validation Fields"
            :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
            @input="onAddField($event)"
            openDirection="below"
            style="width: 20vw; margin-top: 1.5rem"
            selectLabel="Enter"
            track-by="apiName"
            label="referenceDisplayLabel"
          >
            <template slot="noResult">
              <p class="multi-slot">No results. Try loading more</p>
            </template>
            <template slot="afterList">
              <p class="multi-slot__more" @click="onFieldsNextPage">
                Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
              </p>
            </template>
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.svg" alt="" />
                Search for Validation Fields
              </p>
            </template>
          </Multiselect>
        </div>
        <div class="recommend__body" v-if="formType !== 'STAGE_GATING'">
          <Multiselect
            placeholder="Search Fields"
            :options="formFields.list.filter((field) => !addedFieldNames.includes(field.apiName))"
            @input="onAddField($event)"
            openDirection="below"
            style="width: 20vw; margin-top: 1rem"
            selectLabel="Enter"
            track-by="apiName"
            label="referenceDisplayLabel"
          >
            <template slot="noResult">
              <p class="multi-slot">No results. Try loading more</p>
            </template>
            <template slot="afterList">
              <p class="multi-slot__more" @click="onFieldsNextPage">
                Load More <img src="@/assets/images/plusOne.svg" class="invert2" alt="" />
              </p>
            </template>
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.svg" alt="" />
                Search Fields
              </p>
            </template>
          </Multiselect>
        </div>
      </div>

      <div
        style="cursor: not-allowed"
        :class="formType !== 'STAGE_GATING' ? 'collection_fields' : 'stage_fields'"
      >
        <div
          style="
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            margin-top: -0.75rem;
          "
        >
          <div style="display: flex; flex-direction: row; align-items: center">
            <div class="white-background">
              <img src="@/assets/images/logo.png" style="height: 1.5rem" alt="" />
            </div>
            <h3 v-if="resource !== 'OpportunityLineItem' && formType !== 'STAGE_GATING'">
              {{ lowerCase(formType, resource) }}
            </h3>
            <h3 v-else-if="resource === 'OpportunityLineItem'">Product</h3>
            <h3 v-else>Stage Specific</h3>
          </div>

          <div
            style="
              display: flex;
              flex-direction: row;
              align-items: center;
              justify-content: center;
              filter: invert(90%);
            "
          >
            <img src="@/assets/images/share.svg" class="invert2" style="height: 1rem" alt="" />
            <img src="@/assets/images/close.svg" class="invert2" style="height: 1rem; margin-left: 0.5rem" alt="" />
          </div>
        </div>

        <h1 class="example-text">SLACK PREVIEW</h1>
        <div v-if="resource !== 'OpportunityLineItem'">
          <p>Note Subject: <span style="color: #beb5cc">(optional)</span></p>
          <textarea
            disabled
            name=""
            id=""
            cols="30"
            rows="3"
            style="width: 100%; border-radius: 0.25rem; resize: none"
          >
“Meeting Subject goes here” (lives in Tasks)
          </textarea>
        </div>
        <div v-if="resource !== 'OpportunityLineItem'">
          <p>Note: <span style="color: #beb5cc">(optional)</span></p>
          <textarea
            disabled
            name=""
            id=""
            cols="30"
            rows="4"
            style="width: 100%; border-radius: 0.25rem; resize: none"
          >
“Meeting Notes go here” (lives in Tasks)
          </textarea>
        </div>
        <div v-for="field in addedFields" :key="field.id">
          <div
            v-if="
              field.dataType === 'String' ||
              field.dataType === 'Currency' ||
              field.dataType === 'TextArea'
            "
          >
            <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
              {{ field.referenceDisplayLabel }}
            </p>
            <textarea
              disabled
              :class="unshownIds.includes(field.id) ? 'invisible' : ''"
              name=""
              id=""
              cols="30"
              rows="2"
              style="width: 100%; border-radius: 0.25rem"
            >
            </textarea>
          </div>
          <div
            class="drop-row"
            v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'"
          >
            <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
              {{ field.referenceDisplayLabel }}
            </p>
            <select
              :class="unshownIds.includes(field.id) ? 'invisible' : 'drop'"
              disabled
              name="select"
              id=""
            >
              <option value="select">Select</option>
            </select>
          </div>
          <div class="drop-row" v-else-if="field.dataType === 'Date'">
            <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
              {{ field.referenceDisplayLabel }}
            </p>
            <input
              :class="unshownIds.includes(field.id) ? 'invisible' : 'drop'"
              type="date"
              id="start"
              name="trip-start"
              value="0000-00-00"
              disabled
            />
          </div>
          <div class="drop-row" v-else-if="field.dataType === 'DateTime'">
            <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
              {{ field.referenceDisplayLabel }}
            </p>
            <input
              :class="unshownIds.includes(field.id) ? 'invisible' : 'drop'"
              type="datetime-local"
              id="start"
              name="trip-start"
              value="0000-00-00"
              disabled
            />
          </div>
          <div
            class="drop-row"
            v-else-if="field.dataType === 'Phone' || field.dataType === 'Reference'"
          >
            <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
              {{ field.referenceDisplayLabel }}
            </p>
            <input
              :class="unshownIds.includes(field.id) ? 'invisible' : 'drop'"
              type="text"
              disabled
            />
          </div>
          <div
            class="drop-row"
            v-else-if="field.dataType === 'Phone' || field.dataType === 'Double'"
          >
            <p :class="unshownIds.includes(field.id) ? 'invisible' : ''">
              {{ field.referenceDisplayLabel }}
            </p>
            <input
              :class="unshownIds.includes(field.id) ? 'invisible' : 'drop'"
              type="number"
              disabled
            />
          </div>
        </div>
        <div class="example--footer">
          <div style="margin-top: 1rem">
            <button class="close">Close</button>
            <button class="save">Update</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'

import { CollectionManager, Pagination } from '@thinknimble/tn-models'

import ActionChoice from '@/services/action-choices'
import draggable from 'vuedraggable'
import ToggleCheckBox from '@thinknimble/togglecheckbox'

import SlackOAuth from '@/services/slack'
import { SObjectField } from '@/services/salesforce'

import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
    draggable,
    ToggleCheckBox,
    Multiselect: () => import(/* webpackPrefetch: true */ 'vue-multiselect'),
  },
  props: {
    stageForms: {
      type: Array,
      default: () => [],
    },
    customForm: {
      type: Object,
    },
    formType: {
      type: String,
      required: true,
    },
    resource: {
      type: String,
      required: true,
    },
    showValidations: {
      type: Boolean,
      default: false,
    },
    fields: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    managrFields: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      dropdownLoading: false,
      currentStageForm: null,
      formFields: CollectionManager.create({
        ModelClass: SObjectField,
        pagination: { size: 200 },
      }),
      formFieldList: [],
      customSlackFormConfig: [],
      formHasChanges: false,
      savingForm: false,
      addedFields: [],
      removedFields: [],
      ...FORM_CONSTS,
      Pagination,
      meetingType: '',
      actionChoices: [],
      loadingMeetingTypes: false,
      requiredFields: [],
      requiredProductFields: ['PricebookEntryId', 'Quantity'],
      requiredOpportunityFields: ['Name', 'StageName', 'CloseDate'],
      requiredLeadFields: ['LastName', 'Company', 'Status'],
      nameValue: '',
      amountValue: '',
      closeValue: '',
      priceValue: '',
      quantityValue: '',
      lineValue: '',
      lastNameValue: '',
      leadLastNameValue: '',
      companyValue: '',
      accountNameValue: '',
      statusValue: '',
      stageValue: '',
      addingFieldValue: '',
      addingFields: false,
      productSelected: false,
      addingProducts: false,
      noteTitle: {
        _fields: {
          length: {
            defaultVal: null,
            readOnly: false,
          },
          id: {
            defaultVal: '',
            readOnly: true,
          },
          apiName: {
            defaultVal: '',
            readOnly: false,
          },
          custom: {
            defaultVal: false,
            readOnly: false,
          },
          createable: {
            defaultVal: false,
            readOnly: false,
          },
          dataType: {
            defaultVal: '',
            readOnly: false,
          },
          label: {
            defaultVal: '',
            readOnly: false,
          },
          reference: {
            defaultVal: '',
            readOnly: false,
          },
          referenceToInfos: {
            defaultVal: null,
            readOnly: false,
          },
          updateable: {
            defaultVal: false,
            readOnly: false,
          },
          required: {
            defaultVal: false,
            readOnly: false,
          },
          unique: {
            defaultVal: false,
            readOnly: false,
          },
          value: {
            defaultVal: '',
            readOnly: false,
          },
          displayValue: {
            defaultVal: '',
            readOnly: false,
          },
          referenceDisplayLabel: {
            defaultVal: '',
            readOnly: true,
          },
          filterable: {
            defaultVal: '',
            readOnly: true,
          },
          order: {
            defaultVal: null,
            readOnly: false,
          },
          includeInRecap: {
            defaultVal: null,
            readOnly: false,
          },
        },
        length: 30,
        id: '6407b7a1-a877-44e2-979d-1effafec5035',
        apiName: 'meeting_type',
        custom: true,
        createable: true,
        dataType: 'String',
        label: 'Note Subject',
        reference: 'false',
        referenceToInfos: [],
        updateable: true,
        required: false,
        unique: false,
        value: '',
        displayValue: '',
        referenceDisplayLabel: 'Note Subject',
        filterable: 'false',
        order: null,
        includeInRecap: null,
      },
      noteSubject: {
        _fields: {
          length: {
            defaultVal: null,
            readOnly: false,
          },
          id: {
            defaultVal: '',
            readOnly: true,
          },
          apiName: {
            defaultVal: '',
            readOnly: false,
          },
          custom: {
            defaultVal: false,
            readOnly: false,
          },
          createable: {
            defaultVal: false,
            readOnly: false,
          },
          dataType: {
            defaultVal: '',
            readOnly: false,
          },
          label: {
            defaultVal: '',
            readOnly: false,
          },
          reference: {
            defaultVal: '',
            readOnly: false,
          },
          referenceToInfos: {
            defaultVal: null,
            readOnly: false,
          },
          updateable: {
            defaultVal: false,
            readOnly: false,
          },
          required: {
            defaultVal: false,
            readOnly: false,
          },
          unique: {
            defaultVal: false,
            readOnly: false,
          },
          value: {
            defaultVal: '',
            readOnly: false,
          },
          displayValue: {
            defaultVal: '',
            readOnly: false,
          },
          referenceDisplayLabel: {
            defaultVal: '',
            readOnly: true,
          },
          filterable: {
            defaultVal: '',
            readOnly: true,
          },
          order: {
            defaultVal: null,
            readOnly: false,
          },
          includeInRecap: {
            defaultVal: null,
            readOnly: false,
          },
        },
        length: 255,
        id: '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        apiName: 'meeting_comments',
        custom: true,
        createable: true,
        dataType: 'String',
        label: 'Notes',
        reference: 'false',
        referenceToInfos: [],
        updateable: true,
        required: false,
        unique: false,
        value: '',
        displayValue: '',
        referenceDisplayLabel: 'Notes',
        filterable: 'false',
        order: null,
        includeInRecap: null,
      },
    }
  },
  watch: {
    customForm: {
      immediate: true,
      deep: true,
      handler(val) {
        if (val && val.fields.length) {
          this.addedFields = [...val.fieldsRef]
          if (this.formType == 'UPDATE') {
            let currentFormFields = this.addedFields.map((field) => {
              return field.id
            })
            if (currentFormFields.includes('6407b7a1-a877-44e2-979d-1effafec5035') == false) {
              let fieldsToAdd = [this.noteTitle, this.noteSubject]
              let copyArray = this.addedFields
              fieldsToAdd = fieldsToAdd.concat(copyArray)
              this.addedFields = fieldsToAdd.map((field, i) => {
                let altField = { ...field }
                altField.order = i
                if (
                  altField.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  altField.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
                ) {
                  altField.includeInRecap = true
                }
                return altField
              })
            }
          }
          if (this.formType !== 'UPDATE') {
            this.addedFields = this.addedFields.filter((field) => {
              return (
                field.id !== '6407b7a1-a877-44e2-979d-1effafec5035' &&
                field.id !== '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
              )
            })
          }
        }
      },
    },
    resource: {
      async handler(val) {
        if (val) {
          let searchParams = this.formType
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: val,

                ...fieldParam,
              }
              this.formFields.refresh()
              if (this.formType == 'UPDATE') {
                this.onSave()
              }
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },
    formType: {
      immediate: true,

      async handler(val) {
        if (val) {
          let searchParams = val
          if (searchParams.length) {
            let fieldParam = {}
            if (searchParams == this.CREATE) {
              fieldParam['createable'] = true
            } else {
              fieldParam['updateable'] = true
            }
            try {
              this.formFields.filters = {
                salesforceObject: this.resource,

                ...fieldParam,
              }
              this.formFields.refresh()
            } catch (e) {
              console.log(e)
            }
          }
        }
      },
    },
  },
  computed: {
    currentFields() {
      return this.customForm ? this.customForm.fields : []
    },
    addedFieldIds() {
      return this.addedFields.map((field) => {
        return field.id
      })
    },
    addedFieldNames() {
      return this.addedFields.map((field) => {
        return field.apiName
      })
    },
    addedFieldLabels() {
      return this.addedFields.map((field) => {
        return field.referenceDisplayLabel
      })
    },
    unshownIds() {
      return [
        '6407b7a1-a877-44e2-979d-1effafec5035',
        '0bb152b5-aac1-4ee0-9c25-51ae98d55af1',
        'e286d1d5-5447-47e6-ad55-5f54fdd2b00d',
        'fae88a10-53cc-470e-86ec-32376c041893',
      ]
    },
    user() {
      return this.$store.state.user
    },
    userHasProducts() {
      return this.$store.state.user.organizationRef.hasProducts
    },
  },
  created() {
    this.getActionChoices()
  },
  methods: {
    async goToProducts() {
      if (
        (this.resource == 'Opportunity' || this.resource == 'Account') &&
        this.customForm.formType == FORM_CONSTS.MEETING_REVIEW
      ) {
        if (!this.meetingType.length && !this.actionChoices.length) {
          this.$Alert.alert({
            type: 'error',
            message: 'Please enter a Meeting Type',
            timeout: 1000,
          })
          return
        }
      }
      this.savingForm = true

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))

      SlackOAuth.api
        .postOrgCustomForm({
          ...this.customForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
        })
        .then((res) => {
          this.$emit('update:selectedForm', res)
          this.$Alert.alert({
            type: 'success',
            message: 'Form Added Succesfully!',
            timeout: 1000,
          })
        })
        .finally(() => {
          this.savingForm = false
          this.$router.push({ name: 'ProductForm' })
        })
    },
    lowerCase(word1, word2) {
      return (word1 + ' ' + word2)
        .toLowerCase()
        .split(' ')
        .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
        .join(' ')
    },
    productSelect() {
      this.productSelected = !this.productSelected
    },
    getActionChoices() {
      this.loadingMeetingTypes = true
      const action = ActionChoice.api
        .list({})
        .then((res) => {
          this.actionChoices = res.results
        })
        .finally((this.loadingMeetingTypes = false))
    },
    async onFieldsNextPage() {
      this.dropdownLoading = true
      await this.formFields.addNextPage().then(() => {
        setTimeout(() => {
          this.dropdownLoading = false
        }, 1000)
      })
    },
    canRemoveField(field) {
      // If form is create required fields cannot be removed
      // if form is update required fields can be removed
      // if form is meeting review depening on the resource it can/cant be removed
      if (
        this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource] &&
        ~this.MEETING_REVIEW_REQUIRED_FIELDS[this.resource].findIndex((f) => field.id == f)
      ) {
        return false
      } else {
        return true
      }
    },
    onAddField(field) {
      if (this.addedFieldIds.includes(field.id)) {
        this.canRemoveField(field) && this.onRemoveField(field)
        return
      }
      this.addedFields.push({ ...field, order: this.addedFields.length, includeInRecap: true })
      // this.formFields.filters = { salesforceObject: this.resource }
      // this.formFields.refresh()
    },
    goBack() {
      this.$router.push({ name: 'Required' })
    },
    goToOptional() {
      this.$router.push({ name: 'Custom' })
    },
    goToUpdateOpp() {
      this.$router.push({ name: 'UpdateOpportunity' })
    },
    goToValidations() {
      this.$emit('cancel-selected')
    },
    onRemoveField(field) {
      // remove from the array if  it exists

      this.addedFields = [...this.addedFields.filter((f) => f.id != field.id)]

      // if it exists in the current fields add it to remove field

      if (~this.currentFields.findIndex((f) => f == field.id)) {
        this.removedFields = [this.removedFields, field]
      }
    },
    async onSave() {
      if (
        (this.resource == 'Opportunity' || this.resource == 'Account') &&
        this.customForm.formType == FORM_CONSTS.MEETING_REVIEW
      ) {
        if (!this.meetingType.length && !this.actionChoices.length) {
          this.$Alert.alert({
            type: 'error',
            message: 'Please enter a Meeting Type',
            timeout: 1000,
          })
          return
        }
      }
      this.savingForm = true

      let fields = new Set([...this.addedFields.map((f) => f.id)])
      fields = Array.from(fields).filter((f) => !this.removedFields.map((f) => f.id).includes(f))
      let fields_ref = this.addedFields.filter((f) => fields.includes(f.id))

      SlackOAuth.api
        .postOrgCustomForm({
          ...this.customForm,
          fields: fields,
          removedFields: this.removedFields,
          fields_ref: fields_ref,
        })
        .then((res) => {
          this.$emit('update:selectedForm', res)
          this.$Alert.alert({
            type: 'success',
            message: 'Form Added Succesfully!',
            timeout: 1000,
          })
        })
        .finally(() => {
          this.savingForm = false
          if (this.formType !== 'STAGE_GATING') {
            this.$router.push({ name: 'Required' })
          } else {
            this.$router.go()
          }
        })
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

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.section-title {
  letter-spacing: 0.5px;
  border-bottom: 2px solid #e8e8e8;
  padding-bottom: 0.2rem;
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
  &__more {
    background-color: white;
    color: $dark-green;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;

    img {
      height: 0.8rem;
      margin-left: 0.25rem;
      filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
        brightness(93%) contrast(89%);
    }
  }
}
.invert {
  filter: invert(80%);
  height: 1rem;
}
.invert2 {
  filter: invert(80%);
}
.img-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e8e8e8;
  border-radius: 0.2rem;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
}
.label {
  font-size: 0.85rem;
}
.green {
  color: $dark-green;
  font-size: 0.85rem;
}
.default_button {
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;
  border-radius: 0.2rem;
  border: none;
  cursor: pointer;
  color: $dark-green;
  background: white;

  img {
    height: 0.75rem;
    filter: invert(39%) sepia(96%) saturate(373%) hue-rotate(94deg) brightness(75%) contrast(94%);
  }
}
.recommend {
  position: absolute;
  bottom: 20vh;
  left: 34vw;
  z-index: 5;
  background-color: white;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  box-shadow: 1px 2px 2px $very-light-gray;
  height: 40vh;
  width: 30vw;
  &__header {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #e8e8e8;
    height: 4rem;
    padding: 1rem;

    letter-spacing: 0.5px;
    img {
      height: 1rem;
      filter: invert(30%);
    }
  }

  &__body {
    height: 5rem;
    display: flex;
    align-items: flex-start;
    justify-content: space-evenly;
    flex-direction: row;
    margin-top: -0.5rem;
    font-size: 14px;
    padding: 0.5rem;
  }
}
.drop {
  border: 2px solid $soft-gray;
  border-radius: 0.25rem;
  color: $very-light-gray;
  padding: 0.25rem 0.5rem;
  max-height: 2rem;
}
.invisible {
  display: none;
}
.white-background {
  background-color: white;
  border-radius: 0.25rem;
  height: 1.7rem;
  width: 1.7rem;
  margin-right: 0.25rem;
}
#drag {
  filter: invert(60%);
}
#remove {
  filter: invert(60%);
}
.drag-item {
  display: flex;
  align-items: center;
  flex-direction: row;
  padding: 0.2rem 0rem;
  border-radius: 0.2rem;
}
.center {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 0.85rem;
}
.centered {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
}

.slack-form-builder {
  padding: 0rem 3rem;
  color: $base-gray;
}
.slot-icon {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0;
  margin: 0;
  img {
    height: 1rem;
    margin-right: 0.25rem;
    filter: invert(70%);
  }
}
.primary-button {
  padding: 0.4rem 1.5rem;
  box-shadow: none;
  font-weight: 400;
}
.primary-button:disabled {
  background-color: $soft-gray;
}
img:hover {
  cursor: pointer;
}
.close {
  padding: 0.5rem 1.5rem;
  background: transparent;
  color: $very-light-gray;
  border: 2px solid $soft-gray;
  border-radius: 0.25rem;
  opacity: 0.8;
}
.save {
  padding: 0.6rem 1.5rem;
  background-color: $dark-green;
  color: white;
  border: none;
  border-radius: 0.25rem;
  margin-left: 0.5rem;
  cursor: pointer;
}
.disabled {
  padding: 0.5rem 1rem;
  min-width: 6rem;
  background-color: $soft-gray;
  color: $base-gray;
  border: none;
  border-radius: 0.25rem;
  margin-left: 0.5rem;
  opacity: 0.8;
  cursor: text;
}
.disabled__ {
  background-color: transparent;
  font-size: 14px;
  color: $dark-green;
  border: none;
  letter-spacing: 1px;
  cursor: pointer;
}
.example--footer {
  position: sticky;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  margin-top: auto;
  bottom: 0;
  padding: 1rem 0rem;
  background-color: white;
  outline: 1px solid white;
  z-index: 2;
}
.example-text {
  position: absolute;
  bottom: 180px;
  left: 50px;
  opacity: 0.1;
  filter: alpha(opacity=50);
  font-size: 3.5rem;
  transform: rotate(-45deg);
}
.collection_fields {
  background-color: $white;
  padding: 2rem 2rem 0rem 2rem;
  margin: 0.5rem 1rem;
  border-radius: 0.3rem;
  border: 1px solid #e8e8e8;
  overflow: auto;
  height: 72vh;
  width: 42vw;
  display: flex;
  flex-direction: column;
  position: relative;
}
.stage_fields {
  background-color: $white;
  padding: 3rem 1rem;
  margin: -1.5rem 1rem 0rem 0rem;
  border-radius: 0.5rem;
  height: 74vh;
  width: 36vw;
  overflow-y: scroll;
  display: flex;
  flex-direction: column;
  position: relative;
  border: 1px solid #e8e8e8;
}
.opportunity__row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.row__ {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
}
.drop-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
</style>