<template>
  <div class="slack-form-builder">
    <div>
      <div class="slack-from-builder__sf-validations">
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

    <div class="opportunity__row">
      <div :class="formType !== 'STAGE_GATING' ? 'collection_fields' : 'stage_fields'">
        <div v-if="formType === 'STAGE_GATING'">
          <p class="section-title">Add Stage Specific Fields</p>
          <!-- <p style="margin-top: -0.25rem; color: #beb5cc">
            Be sure to save changes before adding another stage!
          </p> -->
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
                <img src="@/assets/images/plusOne.png" alt="" />
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
              >
                <template slot="noResult">
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>

                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
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
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
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
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
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
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
                    Search for 'Last Name'
                  </p>
                </template>
              </Multiselect>
              <!-- :hasNext="!!formFields.pagination.hasNextPage" -->
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
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
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
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
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
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
                    Search for 'Account'
                  </p>
                </template>
              </Multiselect>
            </div>
          </div>
        </div>

        <div v-if="resource === 'Opportunity' && formType !== 'STAGE_GATING'">
          <!-- <div
            v-if="userHasProducts && formType !== 'CREATE'"
            style="margin-bottom: 1rem"
            class="centered"
          >
            <small>
              <span style="color: #41b883">*</span> Need to edit your product form ? Save and
              continue.</small
            >
          </div> -->
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
            >
              <template slot="noResult">
                <p class="multi-slot">No results.</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.png" alt="" />
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
                <p class="multi-slot">No results.</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.png" alt="" />
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
                <p class="multi-slot">No results.</p>
              </template>
              <template slot="afterList">
                <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
              </template>
              <template slot="placeholder">
                <p class="slot-icon">
                  <img src="@/assets/images/search.png" alt="" />
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
                  <p class="multi-slot">No results.</p>
                </template>
                <template slot="afterList">
                  <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
                </template>
                <template slot="placeholder">
                  <p class="slot-icon">
                    <img src="@/assets/images/search.png" alt="" />
                    Search for 'Amount'
                  </p>
                </template>
              </Multiselect>
            </div>

            <div v-if="productSelected">Add products on the next page</div>
          </div>

          <!-- <div
            v-else-if="!addingFields && formType === 'UPDATE'"
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
              Add more fields <img src="@/assets/images/plusOne.png" class="filtered-green" alt="">
            </button>
          </div> -->
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
                  :class="unshownIds.includes(field.id) ? 'invisible' : ''"
                  src="@/assets/images/drag.png"
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
            <img src="@/assets/images/plusOne.png" alt="" />
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
          <!-- 
          <PulseLoadingSpinnerButton
            v-if="resource === 'Account'"
            @click="onSave"
            class="primary-button"
            :class="!addedFieldNames.includes('Name') ? 'primary-button' : 'primary-button'"
            text="Save"
            :loading="savingForm"
            :disabled="!addedFieldNames.includes('Name')"
          /> -->
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
            src="@/assets/images/close.png"
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
            src="@/assets/images/close.png"
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
              <p class="multi-slot">No results.</p>
            </template>
            <template slot="afterList">
              <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
            </template>
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.png" alt="" />
                Search for Validation Fields
              </p>
            </template>
          </Multiselect>
        </div>

        <!-- <div class="recommend__validation" v-if="formType === 'STAGE_GATING'">
            <p style="color: #41b883; font-size: 11px">*Previous Stage Validation Fields</p>
            <div v-if="!orderedStageForm.length">
              <p style="font-size: 14px; text-align: center">Nothing here.. (o^^)o</p>
            </div>
            <div :key="key" v-for="(form, key) in orderedStageForm">
              <div style="margin-top: 1rem">
                <i style="text-transform: uppercase; font-size: 12px; color: #beb5cc"
                  >Fields from <strong>{{ form.stage }}</strong> stage</i
                >
              </div>
              <div class="stages-list">
                <div :key="key" v-for="(val, key) in form.fieldsRef">
                  <p>{{ val.referenceDisplayLabel }}</p>
                </div>
              </div>
            </div>
          </div> -->
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
              <p class="multi-slot">No results.</p>
            </template>
            <template slot="afterList">
              <p class="multi-slot__more" @click="onFieldsNextPage">Load More</p>
            </template>
            <template slot="placeholder">
              <p class="slot-icon">
                <img src="@/assets/images/search.png" alt="" />
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
            <img src="@/assets/images/share.png" style="height: 1rem" alt="" />
            <img src="@/assets/images/clear.png" style="height: 1rem; margin-left: 0.5rem" alt="" />
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
          <!-- <p>{{ field.dataType }}</p> -->
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
import PulseLoadingSpinner from '@thinknimble/pulse-loading-spinner'
import CheckBox from '../../components/CheckBoxUpdated'
import ListItem from '@/components/ListItem'
import ListContainer from '@/components/ListContainer'
import Modal from '@/components/Modal'

import { CollectionManager, Pagination } from '@thinknimble/tn-models'
import CollectionSearch from '@thinknimble/collection-search'

import CustomDropDown from '@/components/CustomDropDown'
import Paginator from '@thinknimble/paginator'
import ActionChoice from '@/services/action-choices'
import draggable from 'vuedraggable'
import ToggleCheckBox from '@thinknimble/togglecheckbox'

import SlackOAuth, { salesforceFields } from '@/services/slack'
import { SObjectField, SObjectValidations, SObjectPicklist } from '@/services/salesforce'

import * as FORM_CONSTS from '@/services/slack'

export default {
  name: 'CustomSlackForm',
  components: {
    PulseLoadingSpinnerButton,
    CheckBox,
    PulseLoadingSpinner,
    Paginator,
    CollectionSearch,
    ListItem,
    ListContainer,
    Modal,

    CustomDropDown,
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
      currentStageForm: null,
      formFields: CollectionManager.create({ ModelClass: SObjectField }),
      formFieldList: [],
      salesforceFields,
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
              let fieldsToAdd = this.managrFields.filter((field) => {
                return (
                  field.id == '6407b7a1-a877-44e2-979d-1effafec5035' ||
                  field.id == '0bb152b5-aac1-4ee0-9c25-51ae98d55af1'
                )
              })
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
    orderedStageForm() {
      let forms = []
      if (this.customForm.stage) {
        let index = this.stageForms.findIndex((f) => f.stage == this.customForm.stage)
        if (~index) {
          forms = this.stageForms.slice(0, index)
        }
      }
      return forms
    },
    sfFieldsAvailableToAdd() {
      return this.fields
    },
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
    selectedFormResourceType() {
      return `${this.formType}.${this.resource}`
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
  // async beforeCreate() {
  //   try {
  //     this.formFields = CollectionManager.create({
  //       ModelClass: SObjectField,
  //       pagination: { size: 500 },
  //     })
  //     this.formFields.refresh()
  //   } catch (e) {
  //     console.log(e)
  //   }
  // },
  methods: {
    test() {
      console.log(this.formFields.list)
      console.log(this.addedFieldNames)
    },

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
    async onSearchFields(v) {
      this.formFields.pagination = new Pagination()
      this.formFields.filters = {
        ...this.formFields.filters,
        search: v,
      }
      await this.formFields.refresh()
    },
    async onFieldsNextPage() {
      await this.formFields.addNextPage()
    },

    nextPage() {
      this.formFields.nextPage()
    },
    previousPage() {
      this.formFields.prevPage()
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
    goToCustomize() {
      this.$router.push({ name: 'CustomizeLandingPage' })
    },
    goToContacts() {
      this.$router.push({ name: 'CreateContacts' })
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
    onMoveFieldUp(field, index) {
      // Disallow move if this is the first field
      if (index === 0) {
        return
      }

      // Make a copy of fields and do the swap
      const newFields = [...this.addedFields]
      newFields[index] = this.addedFields[index - 1]
      newFields[index - 1] = field

      // Apply update to the view model
      this.addedFields = newFields
    },
    onMoveFieldDown(field, index) {
      // Disallow move if this is the last field
      if (index + 1 === this.addedFields.length) {
        return
      }

      // Make a copy of slides and do the swap
      const newFields = [...this.addedFields]
      newFields[index] = this.addedFields[index + 1]
      newFields[index + 1] = field

      // Apply update to the view model
      this.addedFields = newFields
    },

    async updateMeeting(e) {
      if (e.keyCode == 13 && this.meetingType.length) {
        this.loadingMeetingTypes = true
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
          } else {
            const obj = {
              title: this.meetingType,
              organization: this.$store.state.user.organization,
            }

            await ActionChoice.api
              .create(obj)
              .then((res) => {
                this.$Alert.alert({
                  type: 'success',
                  message: 'New meeting type created',
                  timeout: 1000,
                })
              })
              .finally((this.loadingMeetingTypes = false))

            this.getActionChoices()
            this.meetingType = ''
          }
        }
      }
    },
    async removeMeetingType(id) {
      if (!this.$store.state.user.isAdmin) {
        return
      }
      try {
        await ActionChoice.api.delete(id)
        await this.getActionChoices()
      } catch (e) {
        console.log(e)
      } finally {
        this.loadingMeetingTypes = false
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
  font-weight: bold;

  width: 100%;
  padding: 0.5rem 0rem;
  margin: 0;
  &__more {
    background-color: $dark-green;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    border-top: 1px solid #e8e8e8;
    width: 100%;
    padding: 0.75rem 0rem;
    margin: 0;
    cursor: pointer;
  }
}
.invert {
  filter: invert(80%);
  height: 1rem;
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
.center-loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.label {
  font-size: 0.85rem;
}
.green {
  color: $dark-green;
  font-size: 0.85rem;
}
.or_button {
  background: transparent;
  border: none;
  color: white;
  padding-bottom: 0.25rem;
  margin-left: 0.25rem;
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
.name_button {
  font-size: 0px;
  padding: 0.3rem 0.75rem;
  margin-top: 0.5rem;
  border-radius: 0.2rem;
  border: none;
  cursor: pointer;
  color: white;
  background: transparent;
  animation: bounce 0.2s infinite alternate;
}
.name_button::after {
  font-size: 14px;
}

.name_button::after {
  content: 'Name';
}
.name_button:hover::after {
  content: 'Add Name';
}
.name_button:hover {
  background-color: white;
  color: $dark-green !important;
}
.stage_button {
  font-size: 0px;
  padding: 0.3rem 0.75rem;
  margin-top: 0.5rem;
  border-radius: 0.2rem;
  border: none;
  cursor: pointer;
  color: white;
  background: transparent;
  animation: bounce 0.2s infinite alternate;
}
.stage_button::after {
  font-size: 14px;
}
.stage_button::after {
  content: 'Stage';
}
.stage_button:hover::after {
  content: 'Add Stage';
}
.stage_button:hover {
  background-color: white;
  color: $dark-green !important;
}
.closeDate_button {
  font-size: 0px;
  padding: 0.3rem 0.75rem;
  margin-top: 0.5rem;
  border-radius: 0.2rem;
  border: none;
  cursor: pointer;
  color: white;
  background: transparent;
  animation: bounce 0.2s infinite alternate;
}
.closeDate_button::after {
  font-size: 14px;
}

.closeDate_button::after {
  content: 'Close Date';
}
.closeDate_button:hover::after {
  content: 'Add Close Date';
}
.closeDate_button:hover {
  background-color: white;
  color: $dark-green !important;
}
.remove-field {
  border: 1px solid white;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.1rem;
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
  &__validation {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    padding: 0rem 1rem;
  }
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

.margin-top {
  margin-top: 8rem;
}
.field_button {
  padding: 0.3rem 0.75rem;
  margin-top: 0.5rem;
  border-radius: 0.2rem;
  border: none;
  cursor: pointer;
  color: $dark-green;
  background-color: white;
}
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
.drop {
  border: 2px solid $soft-gray;
  border-radius: 0.25rem;
  color: $panther-silver;
  padding: 0.25rem 0.5rem;
  max-height: 2rem;
}
.app {
  background-color: $panther-gray;
  color: $panther-silver;
  border-radius: 0.25rem;
  font-size: 14px;
  padding: 2px;
  margin-left: 0.2rem;
  margin-right: 0.5rem;
}
::v-deep .tn-dropdown__options__option {
  padding-top: 0.375rem;
}
::v-deep .tn-dropdown__selection-container {
  height: 2.5rem;
  box-shadow: none !important;
}
// ::v-deep .tn-dropdown__selection-container:after {
//   position: absolute;
//   content: '';
//   top: 12px;
//   right: 1em;
//   width: 0;
//   height: 0;
//   border: 5px solid transparent;
//   border-color: rgb(173, 171, 171) transparent transparent transparent;
// }
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
.tn-dropdown__selected-items__item-selection--muted {
  font-size: 10px;
}
.filtered-green {
  filter: invert(39%) sepia(96%) saturate(373%) hue-rotate(94deg) brightness(104%) contrast(94%);
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
.option {
  background: transparent;
  color: white;
  padding-bottom: 0.15rem;
  border: none;
  border-bottom: 2px solid $dark-green;
  cursor: pointer;
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
.slack-form-builder
  ::v-deep
  .collection-search
  .collection-search__results
  .collection-search__result-item {
  border: none;
  background-color: $panther;
}
.slack-form-builder
  ::v-deep
  .collection-search
  .collection-search__form
  .collection-search__input
  .search__input {
  @include input-field();
  height: 2.5rem;
  background-color: $panther-silver;
  border: 1px solid $panther-gray;
  width: 10rem;
  padding: 0 0 0 1rem;
  margin: 1rem;
  box-shadow: 1px 4px 7px black;
}

.slack-form-builder {
  // display: flex;
  // flex-direction: column;
  // align-items: flex-start;
  // justify-content: space-evenly;
  padding: 0rem 3rem;
  color: $base-gray;
  &__sf-fields,
  &__sf-validations {
    margin-right: 2rem;
  }

  &__container {
    display: flex;
    background-color: $panther;
  }

  &__sf-field {
    padding: 0.25rem;
    font-size: 0.85rem;
    font-display: #{$bold-font-family};
    background-color: $panther;
    &:hover {
      background-color: $panther;
      cursor: pointer;
      color: $panther-silver;
    }
  }

  &__required {
    padding: 0.25rem;
    font-size: 0.85rem;
    font-display: #{$bold-font-family};
    background-color: $panther;
    &:hover {
      background-color: $panther;
      cursor: pointer;
      color: $panther-orange;
    }
  }

  &__form {
    // flex: 10;
    width: 26vw;
    padding: 2rem;
    box-shadow: 0 5px 10px 0 rgba(132, 132, 132, 0.26);
    background-color: $panther;
    height: 54vh;
    overflow-y: scroll;
    overflow-x: hidden;
    border-radius: 0.5rem;
  }
}
.paginator {
  @include paginator();
  &__container {
    border: none;
    display: flex;
    justify-content: flex-start;
    width: 11rem;
    font-size: 14px;
    margin-top: 1rem;
  }
  &__text {
    width: 6rem;
  }
}
.form-header {
  display: flex;

  align-items: center;

  position: -webkit-sticky;
  position: sticky;
  background-color: $panther;
  top: 0;
  > .save-button {
    flex: 0.5 0 auto;
  }
  > .heading {
    flex: 1 0 auto;
  }
  &__left {
    flex: 9;
  }

  &__right {
    flex: 3;
    display: flex;
    align-items: center;
    justify-content: flex-end;
  }
}
.fields {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.form-field {
  background-color: $panther;
  margin-top: 0.5rem;
  &__left {
    flex: 10;

    display: flex;
    align-items: center;
  }

  &__middle {
    flex: 2;

    display: flex;
    align-items: center;
  }

  &__body {
    font-size: 14px;
  }

  &__label {
  }

  &__right {
    // flex: 2;
    display: flex;
    padding-left: 1rem;
    margin-right: -0.5rem;

    display: flex;
    align-items: center;
  }

  &__btn {
    padding: 0.35rem;
    cursor: pointer;
    color: $dark-gray-blue;

    transition: color 0.3s linear;

    &:hover {
      color: black;
    }

    &--flipped {
      transform: rotateX(180deg);
    }
  }

  &__remove-btn {
    text-align: right;
    color: $coral;
    cursor: pointer;

    &:hover {
      font-weight: 600;
      color: $coral;
    }

    &--disabled {
      color: $dark-gray-blue;
      cursor: initial;

      &:hover {
        font-weight: initial;
        color: initial;
      }
    }
  }
}
.save-button {
  display: flex;
  justify-content: center;
  padding-top: 4rem;
  padding-bottom: 1rem;
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

.field-title {
  font-size: 14px;
  margin-left: 1rem;

  &__bold {
    font-family: #{$bold-font-family};
    margin: 2rem 0 0 1rem;
  }
}

.meeting-type {
  @include input-field();
  padding: 0.5rem;
  width: 15rem;

  &__list {
    margin-top: 0.2rem;
    width: 80%;
    overflow: hidden;
  }
}
.stages-list {
  margin-top: -1rem;
  font-size: 11px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
}

.space {
  margin: 1em;
}
h2 {
  margin: -2px;
  font-size: 1.5rem;
}
.recap {
  display: flex;
  justify-content: flex-end;
  margin-bottom: -2rem;
}
img:hover {
  cursor: pointer;
}
.close {
  padding: 0.5rem 1.5rem;
  background: transparent;
  color: $panther-gray;
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
  color: $panther-gray;
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
.example-footer {
  border-top: 1px solid $very-light-gray;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  margin-top: auto;
  width: 100%;
  height: 10%;
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
::v-deep .multiselect__content {
  max-height: 28vh;
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
  // box-shadow: 3px 4px 7px $very-light-gray;
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
  // box-shadow: 1px 2px 2px $very-light-gray;
}
.fields_title {
  background-color: $panther;
  margin: 1rem;
  padding: 1rem;
  border-radius: 0.5rem;
  width: 100%;
}
.heading {
  background-color: $panther;
}
.opportunity__column {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-right: 2rem;
}
.opportunity__row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}

.required__fields {
  color: $panther-orange;
}

.popular_fields {
  text-align: center;
}
.popularModal {
  color: $panther-silver;
  text-decoration: underline;
  cursor: pointer;
}
.continue__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: $dark-green;
  background-color: white;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-size: 1.02rem;
  margin-right: 0.5rem;
}
.cant__continue {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  background-color: $panther-silver;
  color: $panther-gray;
  cursor: not-allowed;
  height: 2rem;
  width: 10rem;
  font-size: 1.02rem;
  margin-right: 0.5rem;
}
.back__button {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1rem;
  border-radius: 0.3rem;
  line-height: 1.14;
  text-indent: none;
  border-style: none;
  letter-spacing: 0.03rem;
  color: white;
  background-color: $panther-orange;
  cursor: pointer;
  height: 2rem;
  width: 10rem;
  font-size: 1.02rem;
  margin-right: 0.5rem;
}
.warning {
  margin-top: 1rem;
  padding: 0.5rem;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: center;
  color: $panther-gold;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
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