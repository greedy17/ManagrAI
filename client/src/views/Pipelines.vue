<template>
  <div class="pipelines">
    <Modal
      v-if="modalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetNotes()
        }
      "
    >
      <div v-if="notes.length" class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 2rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>

          <div class="close-button">
            <img
              src="@/assets/images/clear.png"
              style="height: 1.2rem"
              @click="resetNotes"
              alt=""
            />
          </div>
        </div>
        <section class="note-section" :key="i" v-for="(note, i) in notes">
          <p class="note-section__title">
            {{ note.saved_data__meeting_type ? note.saved_data__meeting_type + ':' : 'Untitled:' }}
          </p>
          <p class="note-section__body">{{ note.saved_data__meeting_comments }}</p>
        </section>
      </div>

      <div v-else class="modal-container">
        <div class="flex-row-spread">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 2rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h2>Notes</h2>
          </div>
          <div class="close-button">
            <img
              src="@/assets/images/clear.png"
              style="height: 1.2rem"
              @click="resetNotes"
              alt=""
            />
          </div>
        </div>
        <section class="note-section">
          <p class="note-section__title">No notes for this opportunity</p>
        </section>
      </div>
    </Modal>

    <Modal
      v-if="addOppModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetAddOpp()
        }
      "
    >
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.5rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h3>Create Opportunity</h3>
          </div>
          <div class="close-button">
            <img
              src="@/assets/images/clear.png"
              style="height: 1.2rem"
              @click="resetAddOpp"
              alt=""
            />
          </div>
        </div>
        <div class="opp-modal">
          <section :key="field.id" v-for="field in createOppForm">
            <div
              v-if="
                field.dataType === 'TextArea' ||
                (field.dataType === 'String' && field.apiName === 'NextStep')
              "
              class="flex-col"
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="update-input"
                ccols="30"
                rows="4"
                style="width: 30vw; border-radius: 0.4rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.dataType === 'Reference' || field.dataType === 'String'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="text"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>

            <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="update-input"
              >
                <option v-for="(option, i) in picklistQueryOpts[field.apiName]" :key="i">
                  <p>{{ option.label }}</p>
                </option>
              </select>
            </div>

            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="date"
                id="update-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <p>
                {{ field.referenceDisplayLabel }}
              </p>
              <input
                type="datetime-local"
                id="start"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="number"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
          </section>
        </div>
        <div class="flex-end">
          <button class="add-button" @click="createResource">Create Opportunity</button>
        </div>
      </div>
    </Modal>

    <Modal
      v-if="editOpModalOpen"
      dimmed
      @close-modal="
        () => {
          $emit('cancel'), resetEdit()
        }
      "
    >
      <div class="opp-modal-container">
        <div class="flex-row-spread header">
          <div class="flex-row">
            <img
              src="@/assets/images/logo.png"
              style="height: 1.5rem; margin-left: 0.5rem; margin-right: 0.25rem"
              alt=""
            />
            <h3>Update Opportunity</h3>
          </div>

          <div class="close-button">
            <img src="@/assets/images/clear.png" style="height: 1.2rem" @click="resetEdit" alt="" />
          </div>
        </div>

        <div class="opp-modal">
          <section :key="field.id" v-for="field in oppFormCopy">
            <div v-if="field.apiName === 'meeting_type'">
              <p>Note Title:</p>
              <textarea
                id="update-input"
                cols="30"
                rows="2"
                style="width: 30vw; border-radius: 0.4rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div v-else-if="field.apiName === 'meeting_comments'">
              <p>Notes:</p>
              <textarea
                id="update-input"
                ccols="30"
                rows="3"
                style="width: 30vw; border-radius: 0.4rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                field.dataType === 'TextArea' ||
                (field.dataType === 'String' && field.apiName === 'NextStep')
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <textarea
                id="update-input"
                ccols="30"
                rows="4"
                style="width: 30vw; border-radius: 0.4rem"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              >
              </textarea>
            </div>
            <div
              v-else-if="
                (field.dataType === 'String' && field.apiName !== 'meeting_type') ||
                (field.dataType === 'String' && field.apiName !== 'meeting_comments') ||
                (field.dataType === 'String' && field.apiName !== 'NextStep') ||
                field.dataType === 'Reference'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="text"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>

            <div v-else-if="field.dataType === 'Picklist' || field.dataType === 'MultiPicklist'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <select
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
                id="update-input"
              >
                <option v-for="(option, i) in picklistQueryOpts[field.apiName]" :key="i">
                  <p>{{ option.label }}</p>
                </option>
              </select>
            </div>

            <div v-else-if="field.dataType === 'Date'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="date"
                id="update-input"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div v-else-if="field.dataType === 'DateTime'">
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                type="datetime-local"
                id="start"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
            <div
              v-else-if="
                field.dataType === 'Phone' ||
                field.dataType === 'Double' ||
                field.dataType === 'Currency'
              "
            >
              <p>{{ field.referenceDisplayLabel }}:</p>
              <input
                id="update-input"
                type="number"
                @input=";(value = $event.target.value), setUpdateValues(field.apiName, value)"
              />
            </div>
          </section>
        </div>
        <div class="flex-end">
          <p @click="resetEdit" class="cancel">Cancel</p>
          <button @click="updateResource" class="add-button">Update Opportunity</button>
        </div>
      </div>
    </Modal>

    <div v-if="!loading">
      <header class="flex-row-spread">
        <!-- <p style="margin-left: 0.25rem">Pipe Hygeine:</p> -->
        <!-- <div class="stats">
          <p class="closed-deals">Deal closing %:</p>
          <p class="closed-deals">Avg. time to close:</p>
        </div> -->
      </header>

      <section style="margin-bottom: 1rem" class="flex-row-spread">
        <div v-if="!workflowCheckList.length && !primaryCheckList.length" class="flex-row">
          <button @click="showList = !showList" class="select-btn">
            {{ currentList }}
            <img
              v-if="showPopularList"
              class="filter invert"
              style="height: 0.75rem"
              src="@/assets/images/downArrow.png"
              alt=""
            />
          </button>
          <div v-show="showList" class="list-section">
            <p @click="showPopularList = !showPopularList" class="list-section__title">
              Popular Lists
              <img v-if="showPopularList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <button v-if="showPopularList" @click="allOpportunities" class="list-button">
              All Opportunities
              <span class="filter" v-if="currentList === 'All Opportunities'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesThisMonth" class="list-button">
              Closing this month
              <span class="filter" v-if="currentList === 'Closing this month'"> active</span>
            </button>
            <button v-if="showPopularList" @click="closeDatesNextMonth" class="list-button">
              Closing next month
              <span class="filter" v-if="currentList === 'Closing next month'"> active</span>
            </button>
            <p @click="showWorkflowList = !showWorkflowList" class="list-section__title">
              Workflows
              <img v-if="showWorkflowList" src="@/assets/images/downArrow.png" alt="" /><img
                v-else
                src="@/assets/images/rightArrow.png"
                alt=""
              />
            </p>
            <div v-if="showWorkflowList">
              <button
                :key="i"
                v-for="(template, i) in templates.list"
                @click="selectList(template.configs[0], template.title, template.id)"
                class="list-button"
              >
                {{ template.title }}
                <span class="filter" v-if="currentList === template.title"> active</span>
              </button>
            </div>
          </div>
          <button @click="closeFilters" class="add-button">
            <img
              src="@/assets/images/plusOne.png"
              style="height: 1rem; margin-right: 0.25rem"
              alt=""
            />Filter
          </button>
          <h5>
            {{ currentList }}:
            <span>{{ selectedWorkflow ? currentWorkflow.list.length : allOpps.length }}</span>
          </h5>

          <div v-if="filtering" class="filter-section">
            <div class="flex-row-spread wide">
              <p class="filter-section__title">All Filters</p>
              <img @click="closeFilters" class="exit" src="@/assets/images/close.png" alt="" />
            </div>
            <div class="wide" style="display: flex; justify-content: center">
              <div style="margin-left: 0.5rem" class="search-bar wide">
                <input
                  class="wide"
                  type="search"
                  v-model="searchFilterText"
                  placeholder="Search filters"
                />
                <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
              </div>
            </div>

            <small v-if="filterTitle" class="filter-title"
              >{{ filterTitle + ' ' + (filterOption ? filterOption : '') }}:</small
            >
            <div v-if="filterType && !enteringAmount" class="filter-option-section">
              <button
                @click="selectFilterOption(option)"
                class="filter-option-button"
                :key="option"
                v-for="option in monetaryOptions"
              >
                {{ option }}
              </button>
            </div>
            <div v-if="filterType && enteringAmount" class="filter-option-section">
              <input class="search-bar" v-model="amountValue" type="text" />
              <button
                @click="applyAmountFilter"
                :disabled="!amountValue"
                :class="!amountValue ? 'disabled-button' : 'add-button'"
              >
                add
              </button>
            </div>

            <div :key="i" v-for="(filter, i) in filteredFilters" class="filter-section__filters">
              <button
                @click="selectFilter(filter.type, filter.title)"
                style="margin-top: -0.5rem"
                class="list-button"
              >
                <img
                  v-if="filter.type === 'monetary'"
                  src="@/assets/images/monetary.png"
                  class="img"
                  alt=""
                />
                <img
                  v-if="filter.type === 'date'"
                  src="@/assets/images/date.png"
                  class="img"
                  alt=""
                />
                <img
                  v-if="filter.type === 'time'"
                  src="@/assets/images/time.png"
                  class="img"
                  alt=""
                />
                <img
                  v-if="filter.type === 'person'"
                  src="@/assets/images/person.png"
                  class="img"
                  alt=""
                />
                {{ filter.title }}
              </button>
            </div>
          </div>
        </div>
        <div v-else>
          <div class="bulk-action">
            <div v-if="!closeDateSelected && !advanceStageSelected && !forecastSelected">
              <img class="back-logo" src="@/assets/images/logo.png" />
              <!-- <p class="bulk-action__title">Bulk Actions:</p> -->
              <div class="flex-row">
                <button @click="closeDateSelected = !closeDateSelected" class="select-btn">
                  Push Close Date
                  <img
                    src="@/assets/images/date.png"
                    style="height: 1.25rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>

                <button @click="advanceStageSelected = !advanceStageSelected" class="select-btn">
                  Advance Stage
                  <img
                    src="@/assets/images/stairs.png"
                    style="height: 1.25rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
                <button @click="forecastSelected = !forecastSelected" class="select-btn">
                  Change Forecast
                  <img
                    src="@/assets/images/monetary.png"
                    style="height: 1.2rem; margin-left: 0.25rem"
                    alt=""
                  />
                </button>
              </div>
            </div>
            <div class="flex-row-pad" v-if="closeDateSelected">
              <p>How many days ?:</p>
              <input class="number-input" v-model="daysForward" type="number" />

              <button
                :disabled="!daysForward"
                class="add-button"
                @click="pushCloseDates(currentCheckList, daysForward)"
              >
                Push Close Date
              </button>
            </div>

            <div class="flex-row-pad" v-if="advanceStageSelected">
              <p>Select Stage:</p>
              <select
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input=";(value = $event.target.value), setStage(value)"
                id="update-input"
              >
                <option v-for="(stage, i) in allStages" :key="i" :value="stage.value">
                  <p>{{ stage.label }}</p>
                </option>
              </select>

              <button @click="advanceStage(currentCheckList)" class="add-button">
                Advance Stage
              </button>
            </div>

            <div class="flex-row-pad" v-if="forecastSelected">
              <p>Select Forecast:</p>
              <select
                style="margin-left: 0.5rem; margin-right: 0.5rem"
                @input=";(value = $event.target.value), setForecast(value)"
                id="update-input"
              >
                <option v-for="(forecast, i) in allForecasts" :key="i" :value="forecast.value">
                  <p>{{ forecast.label }}</p>
                </option>
              </select>

              <button @click="changeForecast(currentCheckList)" class="add-button">
                Change Forecast
              </button>
            </div>
          </div>
        </div>

        <div class="flex-row">
          <div v-if="!selectedWorkflow" class="search-bar">
            <input type="search" v-model="filterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <div v-else class="search-bar">
            <input type="search" v-model="workflowFilterText" placeholder="search" />
            <img src="@/assets/images/search.png" style="height: 1rem" alt="" />
          </div>
          <button @click="createOppInstance()" class="add-button">
            <img src="@/assets/images/plusOne.png" style="height: 1rem" alt="" />
            Opportunity
          </button>
          <button @click="refresh(refreshId)" class="pipe-button">
            <img src="@/assets/images/refresh.png" class="invert" style="height: 1rem" alt="" />
          </button>
        </div>
      </section>

      <!-- <SkeletonBox width="200px" height="40px" /> -->

      <section v-if="!selectedWorkflow" class="table-section">
        <div class="table">
          <div class="table-row">
            <div style="padding: 2vh" class="table-cell-checkbox table-cell-header">
              <div>
                <input @click="onCheckAll" type="checkbox" id="checkAllPrimary" />
                <label for="checkAllPrimary"></label>
              </div>
            </div>
            <div class="table-cell-header">Name</div>
            <div class="table-cell-header" :key="i" v-for="(field, i) in oppFields" ref="fields">
              {{ field.referenceDisplayLabel }}
            </div>
            <div class="table-cell-header cell-name">
              <img src="@/assets/images/plusOne.png" class="invert" style="height: 1rem" alt="" />
              <!-- <p style="color: #9b9b9b">(coming soon)</p> -->
            </div>
          </div>

          <tr class="table-row" :key="i" v-for="(opp, i) in allOppsFiltered">
            <div
              :class="
                primaryCheckList.includes(opp.id)
                  ? 'table-cell-checkbox selected'
                  : 'table-cell-checkbox'
              "
            >
              <div>
                <input type="checkbox" :id="i" v-model="primaryCheckList" :value="opp.id" />
                <label :for="i"></label>
              </div>
            </div>
            <div
              :class="
                primaryCheckList.includes(opp.id) ? 'table-cell-selected' : 'table-cell cell-name'
              "
            >
              <div class="flex-row-spread">
                <div>
                  {{ opp.name }}
                  <span style="color: #199e54; margin-left: 0.2rem">account name</span>
                  <div style="color: #9b9b9b">owner: owner's name</div>
                </div>
                <div style="margin-top: 0.5rem" class="flex-row">
                  <img
                    @click="createFormInstance(opp.id)"
                    class="name-cell-note-button"
                    src="@/assets/images/edit-note.png"
                  />
                  <img
                    @click="getNotes(opp.id)"
                    class="name-cell-edit-note-button"
                    src="@/assets/images/white-note.png"
                    :id="opp.id"
                  />
                </div>
              </div>
            </div>

            <div
              :key="i"
              v-for="(field, i) in oppFields"
              :class="primaryCheckList.includes(opp.id) ? 'table-cell-selected' : 'table-cell'"
            >
              <p v-if="field.apiName !== 'Amount'">
                {{
                  opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                    ? opp['secondary_data'][capitalizeFirstLetter(camelize(field.apiName))]
                    : '---'
                }}
              </p>

              <p style="color: #199e54" v-else>
                {{
                  opp[lowercaseFirstLetter(camelize(field.apiName))]
                    ? formatCash(parseFloat(opp[lowercaseFirstLetter(camelize(field.apiName))]))
                    : '$ ---'
                }}
              </p>
            </div>
            <div class="table-cell">
              <p>---</p>
            </div>
          </tr>
        </div>
      </section>

      <section v-if="selectedWorkflow && currentWorkflow.list.length > 0" class="table-section">
        <div class="table">
          <div class="table-row">
            <div class="table-cell-checkbox-header">
              <div>
                <input
                  @click="onCheckAllWorkflows"
                  type="checkbox"
                  value="1"
                  id="checkAllWorkflow"
                />
                <label for="checkAllWorkflow"></label>
              </div>
            </div>
            <div class="table-cell-header">Name</div>
            <div class="table-cell-header" :key="i" v-for="(field, i) in oppFields" ref="fields">
              {{ getFields(field.referenceDisplayLabel) }}
            </div>
            <div class="table-cell-header cell-name">
              <img src="@/assets/images/plusOne.png" class="invert" style="height: 1rem" alt="" />
            </div>
          </div>

          <tr class="table-row" :key="i" v-for="(workflow, i) in filteredWorkflows">
            <div class="table-cell-checkbox">
              <div>
                <input
                  type="checkbox"
                  :id="i"
                  v-model="workflowCheckList"
                  :value="workflow.resourceRef.id"
                />
                <label :for="i"></label>
              </div>
            </div>
            <div class="table-cell cell-name">
              <div class="flex-row-spread">
                <div>
                  {{ workflow.resourceRef.name }}
                  <span style="color: #199e54; margin-left: 0.2rem">account name</span>
                  <div style="color: #9b9b9b">owner: owner's name</div>
                </div>
                <div style="margin-top: 0.5rem" class="flex-row">
                  <img
                    @click="createFormInstance(workflow.resourceRef.id)"
                    class="name-cell-note-button"
                    src="@/assets/images/edit-note.png"
                  />
                  <img
                    @click="getNotes(workflow.resourceRef.id)"
                    class="name-cell-edit-note-button"
                    src="@/assets/images/white-note.png"
                  />
                </div>
              </div>
            </div>

            <!-- <div :key="field" v-for="field in currentWorkflowFields" class="table-cell">
              {{ workflow.resourceRef[camelize(field)] }}
            </div> -->

            <div :key="field.name" v-for="field in currentWorkflowFields" class="table-cell">
              <p v-if="field !== 'Amount'">
                {{
                  field === 'Stage'
                    ? workflow.resourceRef.secondaryData[
                        capitalizeFirstLetter(camelize(field + 'Name'))
                      ]
                    : workflow.resourceRef.secondaryData[capitalizeFirstLetter(camelize(field))]
                    ? workflow.resourceRef.secondaryData[capitalizeFirstLetter(camelize(field))]
                    : '---'
                }}
              </p>

              <p style="color: #199e54" v-else>
                {{
                  workflow.resourceRef.secondaryData[capitalizeFirstLetter(camelize(field))]
                    ? formatCash(
                        parseFloat(
                          workflow.resourceRef.secondaryData[
                            capitalizeFirstLetter(camelize(field))
                          ],
                        ),
                      )
                    : '$ ---'
                }}
              </p>
            </div>
            <div class="table-cell">
              <p>---</p>
            </div>
          </tr>
        </div>
      </section>

      <section
        v-if="currentWorkflow && currentWorkflow.list.length < 1"
        class="empty-table-section"
      >
        <div class="empty-table">
          <div class="table-row">
            <div class="flex-row table-cell-header">
              <h5 style="margin-left: 1rem">
                No results for the {{ currentList }} workflow. Try refreshing
              </h5>
              <button @click="refresh(refreshId)" class="centered__button">
                <img src="@/assets/images/refresh.png" style="height: 0.75rem" alt="" />
              </button>
            </div>
            <!-- <div :key="field.id" v-for="field in oppFormCopy" class="table-cell-header">
              <p v-if="field.apiName !== 'meeting_type' && field.apiName !== 'meeting_comments'">
                {{ field.referenceDisplayLabel }}
              </p>
            </div> -->
          </div>
        </div>
      </section>
    </div>
    <div class="loader" v-if="loading">
      <img src="@/assets/images/loading-gif.gif" class="invert" style="height: 8rem" alt="" />
    </div>
  </div>
</template>

<script>
import DropDownSelect from '@thinknimble/dropdownselect'
import { SObjects, SObjectPicklist } from '@/services/salesforce'
import AlertTemplate, { AlertConfig, AlertInstance } from '@/services/alerts/'
import SkeletonBox from '@/components/SkeletonBox'
import CollectionManager from '@/services/collectionManager'
import SlackOAuth, { salesforceFields } from '@/services/slack'
import DropDownSearch from '@/components/DropDownSearch'
import Modal from '@/components/InviteModal'
import User from '@/services/users'

export default {
  name: 'Pipelines',
  components: {
    DropDownSelect,
    Modal,
    DropDownSearch,
    SkeletonBox,
  },
  data() {
    return {
      primaryCheckList: [],
      workflowCheckList: [],
      closeDateSelected: false,
      advanceStageSelected: false,
      forecastSelected: false,
      selection: false,
      allStages: [],
      allForecasts: [],
      newStage: null,
      newForecast: null,
      originalList: null,
      daysForward: null,
      allOpps: null,
      loading: false,
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
      team: CollectionManager.create({ ModelClass: User }),
      currentWorkflow: null,
      currentWorkflowFields: null,
      selectedWorkflow: false,
      modalOpen: false,
      editOpModalOpen: false,
      addOppModalOpen: false,
      refreshId: null,
      filterText: '',
      workflowFilterText: '',
      searchFilterText: '',
      currentList: 'All Opportunities',
      showList: false,
      showWorkflowList: true,
      showPopularList: true,
      filtering: false,
      filterType: null,
      filterTitle: null,
      filterOption: null,
      enteringAmount: false,
      amountValue: null,
      todaysAlerts: null,
      todaysList: null,
      todaysTemplate: null,
      showNotes: false,
      notes: [],
      updateOppForm: null,
      oppFormCopy: null,
      createOppForm: null,
      oppFields: [],
      instances: [],
      instanceId: null,
      formData: {},
      noteTitle: '',
      noteInfo: '',
      verboseName: null,
      taskHash: null,
      monetaryOptions: ['less than', 'greater than', 'equals'],
      picklistQueryOpts: {},
      instanceIds: [],
      oppFilters: [
        {
          title: 'Amount',
          type: 'monetary',
        },
        {
          title: 'Close date',
          type: 'date',
        },
        {
          title: 'Next step date',
          type: 'date',
        },
        {
          title: 'Last activity',
          type: 'time',
        },
        {
          title: 'Last modified',
          type: 'time',
        },
        {
          title: 'Owner',
          type: 'person',
        },
      ],
    }
  },
  computed: {
    currentCheckList() {
      if (this.primaryCheckList.length > 0) {
        return this.primaryCheckList
      } else if (this.workflowCheckList.length > 0) {
        return this.workflowCheckList
      } else {
        return []
      }
    },
    user() {
      return this.$store.state.user
    },
    allOppsFiltered() {
      return this.allOpps.filter((opp) =>
        opp.name.toLowerCase().includes(this.filterText.toLowerCase()),
      )
    },
    filteredWorkflows() {
      return this.currentWorkflow.list.filter((opp) =>
        opp.resourceRef.name.toLowerCase().includes(this.workflowFilterText.toLowerCase()),
      )
    },
    filteredFilters() {
      return this.oppFilters.filter((opp) =>
        opp.title.toLowerCase().includes(this.searchFilterText.toLowerCase()),
      )
    },
    currentMonth() {
      let date = new Date()
      return date.getMonth()
    },
  },
  created() {
    this.templates.refresh()
    this.getObjects()
    this.getAllForms()
    this.listStages()
    this.listForecast()
    this.team.refresh()
  },
  watch: {
    primaryCheckList: 'closeAll',
    workflowCheckList: 'closeAll',
  },
  methods: {
    closeAll() {
      if (this.primaryCheckList.length === 0 || this.workflowCheckList === 0) {
        this.closeDateSelected = false
        this.advanceStageSelected = false
        this.forecastSelected = false
        console.log('works')
      }
    },
    setStage(val) {
      this.newStage = val
    },
    setForecast(val) {
      this.newForecast = val
    },
    test() {
      console.log(this.templates.list)
    },
    onCheckAll() {
      if (this.primaryCheckList.length < 1) {
        for (let i = 0; i < this.allOppsFiltered.length; i++) {
          this.primaryCheckList.push(this.allOppsFiltered[i].id)
        }
      } else {
        this.primaryCheckList = []
      }
    },
    onCheckAllWorkflows() {
      if (this.workflowCheckList.length < 1) {
        for (let i = 0; i < this.filteredWorkflows.length; i++) {
          this.workflowCheckList.push(this.filteredWorkflows[i].resourceRef.id)
        }
      } else {
        this.workflowCheckList = []
      }
    },
    getIndex(val) {
      let index = 0
      for (let i = 0; i < this.picklistQueryOpts.length; i++) {
        this.picklistQueryOpts[i] === val ? (index = i) : (index = null)
      }
      return index
    },
    async listPicklists(type, query_params) {
      try {
        const res = await SObjectPicklist.api.listPicklists(query_params)
        this.picklistQueryOpts[type] = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listStages() {
      try {
        const res = await SObjectPicklist.api.listPicklists({
          salesforceObject: 'Opportunity',
          picklistFor: 'StageName',
        })
        this.allStages = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async listForecast() {
      try {
        const res = await SObjectPicklist.api.listPicklists({
          salesforceObject: 'Opportunity',
          picklistFor: 'ForecastCategoryName',
        })
        this.allForecasts = res.length ? res[0]['values'] : []
      } catch (e) {
        console.log(e)
      }
    },
    async refresh(id) {
      if (id) {
        try {
          await AlertTemplate.api.runAlertTemplateNow(id)
          this.$Alert.alert({
            message: `workflow initiated successfully`,
            sub: 'Refresh to see changes',
            type: 'success',
            timeout: 2000,
          })
        } catch {
          this.$Alert.alert({
            message: 'Something went wrong (o^^)o.... Try again',
            type: 'error',
            timeout: 2000,
          })
        }
      }
      setTimeout(() => {
        this.getObjects()
        this.getAllForms()
      }, 200)
    },
    resetNotes() {
      this.modalOpen = !this.modalOpen
      this.notes = []
    },
    resetEdit() {
      this.editOpModalOpen = !this.editOpModalOpen
    },
    resetAddOpp() {
      this.addOppModalOpen = !this.addOppModalOpen
    },
    camelize(str) {
      return str.replace(/(?:^\w|[A-Z]|\b\w|\s+)/g, function (match, index) {
        if (+match === 0) return ''
        return index === 0 ? match.toLowerCase() : match.toUpperCase()
      })
    },
    snakeCase(string) {
      return string
        .replace(/\W+/g, ' ')
        .split(/ |\B(?=[A-Z])/)
        .map((word) => word.toLowerCase())
        .join('_')
    },
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1)
    },
    lowercaseFirstLetter(string) {
      if (string) {
        return string.charAt(0).toLowerCase() + string.slice(1)
      }
    },
    getFields(field) {
      while (!this.currentWorkflowFields.includes(field)) {
        this.currentWorkflowFields.push(field)
      }
      return field
    },
    async createFormInstance(id) {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'UPDATE',
          resourceId: id,
        })
        this.editOpModalOpen = true
        this.instanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    async createOppInstance() {
      try {
        const res = await SObjects.api.createFormInstance({
          resourceType: 'Opportunity',
          formType: 'CREATE',
        })
        this.addOppModalOpen = true
        console.log(res.form_id)
        this.instanceId = res.form_id
      } catch (e) {
        console.log(e)
      }
    },
    futureDate(val) {
      let currentDate = new Date()
      currentDate.setDate(currentDate.getDate() + Number(val))
      let currentDayOfMonth = currentDate.getDate()
      let currentMonth = currentDate.getMonth()
      let currentYear = currentDate.getFullYear()
      let dateString = currentYear + '-' + (currentMonth + 1) + '-' + currentDayOfMonth
      return dateString
    },
    pushCloseDates(ids, val) {
      this.instanceIds = []
      let data = this.futureDate(val)
      this.createBulkInstance(ids)
      setTimeout(() => {
        this.bulkUpdateCloseDate(this.instanceIds, data)
      }, 100)
    },
    advanceStage(ids) {
      this.instanceIds = []
      this.createBulkInstance(ids)
      setTimeout(() => {
        this.bulkUpdateStage(this.instanceIds, this.newStage)
      }, 100)
    },
    changeForecast(ids) {
      this.instanceIds = []
      this.createBulkInstance(ids)
      setTimeout(() => {
        this.bulkChangeForecast(this.instanceIds, this.newForecast)
      }, 100)
    },
    async createBulkInstance(ids) {
      this.loading = true
      for (let i = 0; i < ids.length; i++) {
        try {
          const res = await SObjects.api.createFormInstance({
            resourceType: 'Opportunity',
            formType: 'UPDATE',
            resourceId: ids[i],
          })
          this.instanceIds.push(res.form_id)
        } catch (e) {
          console.log(e)
        }
      }
    },
    setUpdateValues(key, val) {
      if (val) {
        this.formData[key] = val
      }
    },
    async bulkUpdateCloseDate(ids, data) {
      for (let i = 0; i < ids.length; i++) {
        try {
          const res = await SObjects.api.updateResource({
            form_id: ids[i],
            form_data: { CloseDate: data },
          })
        } catch (e) {
          console.log(e)
        }
      }
      this.primaryCheckList = []
      this.workflowCheckList = []
      this.closeDateSelected = false
      this.loading = false
      this.$Alert.alert({
        type: 'success',
        timeout: 3000,
        message: 'Salesforce update successful!',
        sub: 'Refresh to see changes',
      })
    },
    async bulkUpdateStage(ids, data) {
      for (let i = 0; i < ids.length; i++) {
        try {
          const res = await SObjects.api.updateResource({
            form_id: ids[i],
            form_data: { StageName: data },
          })
        } catch (e) {
          console.log(e)
        }
      }
      console.log(data)
      this.primaryCheckList = []
      this.workflowCheckList = []
      this.advanceStageSelected = false
      this.loading = false
      this.$Alert.alert({
        type: 'success',
        timeout: 3000,
        message: 'Salesforce update successful!',
        sub: 'Refresh to see changes',
      })
    },
    async bulkChangeForecast(ids, data) {
      for (let i = 0; i < ids.length; i++) {
        try {
          const res = await SObjects.api.updateResource({
            form_id: ids[i],
            form_data: { ForecastCategoryName: data },
          })
        } catch (e) {
          console.log(e)
        }
      }
      console.log(data)
      this.primaryCheckList = []
      this.workflowCheckList = []
      this.forecastSelected = false
      this.loading = false
      this.$Alert.alert({
        type: 'success',
        timeout: 3000,
        message: 'Salesforce update successful!',
        sub: 'Refresh to see changes',
      })
    },
    async updateResource() {
      this.loading = true
      this.editOpModalOpen = false
      try {
        const res = await SObjects.api.updateResource({
          form_id: this.instanceId,
          form_data: this.formData,
        })
        //  this.$router.go()
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Salesforce update successful!',
          sub: 'Refresh to see changes',
        })
      } catch (e) {
        console.log(e)
      }
      this.getObjects()
    },
    async createResource() {
      this.loading = true
      this.addOppModalOpen = false
      try {
        const res = await SObjects.api.createResource({
          form_id: this.instanceId,
          form_data: this.formData,
        })
        console.log(res)
        this.$Alert.alert({
          type: 'success',
          timeout: 3000,
          message: 'Opportunity created successfully!',
          sub: 'Refresh to see changes',
        })
      } catch (e) {
        console.log(e)
      }
      this.getObjects()
    },
    async confirmUpdate() {
      try {
        const res = await SObjects.api.confirmUpdate({
          verbose_name: this.verboseName,
          task_hash: this.taskHash,
        })
        console.log(res)
      } catch (e) {
        console.log(e)
      }
    },
    selectList(configId, title, id) {
      this.currentWorkflowFields = []
      this.refreshId = id
      this.currentWorkflow = CollectionManager.create({
        ModelClass: AlertInstance,
        filters: {
          byConfig: configId,
        },
      })
      this.currentWorkflow.refresh()
      this.currentList = title
      this.selectedWorkflow = true
      this.showList = false
    },
    showAlertList() {
      this.allOpps = this.alertList
    },
    async getConfigs(configId) {
      try {
        const res = await AlertConfig.api.getCurrentInstances({
          configId: configId,
        })
        this.todaysAlerts = res.data.instances
        this.todaysTemplate = res.data.template
      } catch (e) {
        console.log(e)
      } finally {
      }
    },
    async getAllForms() {
      this.loading = true
      try {
        let res = await SlackOAuth.api.getOrgCustomForm()
        this.updateOppForm = res.filter(
          (obj) => obj.formType === 'UPDATE' && obj.resource === 'Opportunity',
        )
        this.createOppForm = res.filter(
          (obj) => obj.formType === 'CREATE' && obj.resource === 'Opportunity',
        )
        this.oppFormCopy = this.updateOppForm[0].fieldsRef
        this.createOppForm = this.createOppForm[0].fieldsRef
        for (let i = 0; i < this.oppFormCopy.length; i++) {
          if (
            this.oppFormCopy[i].dataType === 'Picklist' ||
            this.oppFormCopy[i].dataType === 'MultiPicklist'
          ) {
            this.picklistQueryOpts[this.oppFormCopy[i].apiName] = this.oppFormCopy[i].apiName
          }
        }
        for (let i in this.picklistQueryOpts) {
          this.picklistQueryOpts[i] = this.listPicklists(i, { picklistFor: i })
        }

        this.oppFields = this.updateOppForm[0].fieldsRef.filter(
          (field) =>
            field.apiName !== 'meeting_type' &&
            field.apiName !== 'meeting_comments' &&
            field.apiName !== 'Name',
        )
      } catch (error) {
        console.log(error)
      }
      this.loading = false
    },
    async getObjects() {
      this.loading = true
      try {
        const res = await SObjects.api.getObjects('Opportunity')
        this.allOpps = res.results
        this.originalList = res.results
        this.todaysList = res.results
      } catch {
        this.$Alert.alert({
          type: 'error',
          timeout: 2000,
          message: 'There was an error collecting objects',
        })
      }
      this.loading = false
    },
    async getNotes(id) {
      try {
        const res = await SObjects.api.getNotes({
          resourceId: id,
        })
        this.modalOpen = true

        if (res.length) {
          for (let i = 0; i < res.length; i++) {
            this.notes.push(res[i])
          }
        }
      } catch (e) {
        console.log(e)
      }
    },

    async handleCancel() {
      await this.refresh()
      this.resetNotes()
      this.$emit('cancel')
    },
    addOpp() {
      this.addOppModalOpen = true
    },
    applyAmountFilter() {
      // this.allOpps = this.allOpps.filter((opp) => opp.amount > this.amountValue)
    },
    showAmount() {
      console.log(this.amountValue)
    },
    selectFilter(type, title) {
      switch (type) {
        case 'monetary':
          this.monetaryFilter(type, title)
          break
        case 'date':
          this.dateFilter(type, title)
          break
        case 'time':
          this.timeFilter(type, title)
          break
        case 'person':
          this.personFilter(type, title)
          break
      }
    },
    selectFilterOption(option) {
      if (option === 'less than' || option === 'greater than' || option === 'equals') {
        this.amountInput(option)
      }
    },
    amountInput(option) {
      this.enteringAmount = !this.enteringAmount
      this.filterOption = option
    },
    monetaryFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    dateFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    timeFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    personFilter(type, title) {
      this.filterType = type
      this.filterTitle = title
    },
    closeFilters() {
      this.showList ? (this.showList = !this.showList) : (this.showList = this.showList)
      this.filtering = !this.filtering
    },
    closeDatesThisMonth() {
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth,
      )
      this.currentList = 'Closing this month'
      this.showList = !this.showList
    },
    closeDatesNextMonth() {
      this.allOpps = this.originalList
      this.selectedWorkflow = false
      this.allOpps = this.allOpps.filter(
        (opp) => new Date(opp.close_date).getMonth() == this.currentMonth + 1,
      )
      this.currentList = 'Closing next month'
      this.showList = !this.showList
    },
    allOpportunities() {
      this.selectedWorkflow = false
      this.allOpps = this.originalList
      this.currentList = 'All Opportunities'
      this.showList = !this.showList
    },
    closeList() {
      if (this.showList === false) {
        this.showList = this.showList
      } else {
        this.showList = !this.showList
      }
    },
    formatDate(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      return input.replace(pattern, '$2/$3/$1')
    },
    formatDateTime(input) {
      var pattern = /(\d{4})\-(\d{2})\-(\d{2})/
      if (!input || !input.match(pattern)) {
        return null
      }
      let newDate = input.replace(pattern, '$2/$3/$1')
      return newDate.split('T')[0]
    },
    formatCash(money) {
      let cash = new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        //maximumFractionDigits: 0, // (2500.99 would be printed as $2,501)
      })
      if (money) {
        return cash.format(money)
      }
      return '-'
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

.closed-deals {
}
.stats {
  padding-left: 0.25rem;
}
.select-btn {
  border: none;
  min-height: 4.5vh;
  padding: 0.5rem 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 1px 1px 2px $very-light-gray;
  border-radius: 0.25rem;
  background-color: white;
  cursor: pointer;
  color: $darker-green;
  font-weight: 900px;
  margin-right: 0.5rem;

  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
input[type='checkbox']:checked + label::after {
  content: '';
  position: absolute;
  width: 1ex;
  height: 0.3ex;
  background: rgba(0, 0, 0, 0);
  top: 0.9ex;
  left: 0.4ex;
  border: 2px solid $dark-green;
  border-top: none;
  border-right: none;
  -webkit-transform: rotate(-45deg);
  -moz-transform: rotate(-45deg);
  -o-transform: rotate(-45deg);
  -ms-transform: rotate(-45deg);
  transform: rotate(-45deg);
}

input[type='checkbox'] {
  line-height: 2.1ex;
}

input[type='radio'],
input[type='checkbox'] {
  position: absolute;
  left: -999em;
}

input[type='checkbox'] + label {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

input[type='checkbox'] + label::before {
  content: '';
  display: inline-block;
  vertical-align: -22%;
  height: 1.75ex;
  width: 1.75ex;
  background-color: white;
  border: 1px solid rgb(182, 180, 180);
  border-radius: 4px;
  margin-right: 0.5em;
}

::placeholder {
  color: $mid-gray;
}
input[type='date']::-webkit-datetime-edit-text,
input[type='date']::-webkit-datetime-edit-month-field,
input[type='date']::-webkit-datetime-edit-day-field,
input[type='date']::-webkit-datetime-edit-year-field {
  color: #888;
  cursor: pointer;
  padding-left: 0.5rem;
}

h3 {
  font-size: 22px;
}
::v-deep .tn-dropdown__selection-container:after {
  position: absolute;
  content: '';
  top: 13px;
  right: 1em;
  width: 0;
  height: 0;
  border: 5px solid transparent;
  border-color: $base-gray transparent transparent transparent;
}
::v-deep .tn-dropdown__selection-container {
  width: 12vw;
  height: 4.5vh;
  border: 1px solid $soft-gray;
  box-shadow: 1px 2px 1px $very-light-gray;
  padding: 0.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
}
::v-deep .tn-dropdown--medium {
  display: flex;
  justify-content: center;
  width: 12vw;
  height: 4.5vh;
  margin-right: 1rem;
}
::v-deep .tn-dropdown__selected-items__item-selection--muted {
  color: $base-gray;
}
::v-deep .tn-dropdown__options__option--selected {
  color: $base-gray;
  background-color: white;
  border-radius: 0.25rem;
}
.table-section {
  height: 80vh;
  overflow: scroll;
  margin-top: 0.5rem;
  border-radius: 5px;
  box-shadow: 1px 1px 20px 1px $soft-gray;
  background-color: $off-white;
}
.empty-table-section {
  height: 30vh;
  margin-top: 2rem;
  border-radius: 5px;
  box-shadow: 1px 1px 20px 1px $soft-gray;
  background-color: $off-white;
}
.table {
  display: table;
  width: 99vw;
}
.empty-table {
  display: table;
  width: 98vw;
}
.table-row {
  display: table-row;
}
.table-cell {
  display: table-cell;
  background-color: $off-white;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.selected {
  // background-color: white;
}
.table-cell-selected {
  display: table-cell;
  background-color: white;
  color: $darker-green;
  padding: 3vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
  font-size: 13px;
}
.table-cell:hover {
  cursor: text;
  background-color: white;
}
.modal-container {
  background-color: $white;
  min-height: 60vh;
  align-items: center;
  border-radius: 0.5rem;
  padding: 0.25rem;
}
.close-button {
  border-radius: 50%;
  background-color: $lighter-green;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.5rem;
  margin-top: -1rem;
  padding: 0.25rem;
  cursor: pointer;
  img {
    filter: invert(50%) sepia(20%) saturate(1581%) hue-rotate(94deg) brightness(93%) contrast(90%);
  }
}
.opp-modal-container {
  background-color: white;
  height: 80vh;
  align-items: center;
  border-radius: 0.6rem;
  padding: 0.5rem;
}
.opp-modal {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.5rem;
  overflow-y: scroll;
  height: 56vh;
  border-radius: 0.25rem;
  border-bottom: 3px solid $white;
  letter-spacing: 1px;
  color: $darker-green;
  font-weight: bold;

  div {
    margin-right: 1rem;
  }
}

.note-section {
  padding: 0.5rem 1rem;
  margin-bottom: 0.25rem;
  background-color: white;
  border-bottom: 1px solid $soft-gray;
  overflow: scroll;
  &__title {
    font-size: 16px;
    font-weight: bold;
    color: $dark-green;
    letter-spacing: 1px;
  }
  &__body {
    color: $base-gray;
  }
}
.table-cell-checkbox {
  display: table-cell;
  padding: 2vh;
  border: none;
  border-bottom: 1px solid $soft-gray;
}
.table-cell-header {
  display: table-cell;
  padding: 3vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  border-radius: 2px;
  z-index: 1;
  top: 0;
  position: sticky;
  background-color: $off-white;
  font-weight: bold;
  font-size: 14px;
  color: $base-gray;
}
.table-cell-checkbox-header {
  display: table-cell;
  padding: 2vh 1vh;
  border: none;
  border-bottom: 3px solid $light-orange-gray;
  z-index: 1;
  top: 0;
  position: sticky;
  background-color: $off-white;
}
.table-row:nth-child(even) {
  background: $off-white;
}
.cell-name {
  background-color: white;
}
input[type='search'] {
  border: none;
  background-color: $off-white;
  padding: 4px;
  margin: 0;
}
input[type='search']:focus {
  outline: none;
}
input[type='text']:focus {
  outline: none;
}
input[type='checkbox'] {
  cursor: pointer;
}
select {
  color: #9e9e9e;
  cursor: pointer;
}
option:not(:first-of-type) {
  color: black;
}
p {
  font-size: 13px;
}
.img {
  margin-right: 0.25rem;
  height: 0.75rem;
  filter: invert(50%);
}

header,
section {
  margin: 0;
  padding: 0px 2px;
}
.flex-row {
  position: relative;
  display: flex;
  flex-direction: row;
  align-items: center;
}
.flex-row-pad {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 0rem 0.5rem;
}
.bulk-action {
  margin: 0.75rem 0rem;
  &__title {
    font-weight: bold;
    font-size: 14px;
    margin-left: 0.25rem;
  }
}
.back-logo {
  position: absolute;
  opacity: 0.06;
  filter: alpha(opacity=50);
  height: 10%;
  right: 0;
}
.flex-col {
  display: flex;
  flex-direction: column;
}
.flex-row-spread {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}
.pipelines {
  margin-top: 5rem;
  color: $base-gray;
  height: 94vh;
  overflow: hidden;
}
.invert {
  filter: invert(80%);
}
.sub-heading {
  color: $gray;
  margin-top: -1vh;
}
.title {
  color: $base-gray;
}
.pipe-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  // box-shadow: 1px 2px 3px $very-light-gray;
  background-color: $lighter-green;
  border: none;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.5rem;
  border-radius: 0.2rem;
  color: $darker-green;
  cursor: pointer;
  transition: all 0.3s;
}
.pipe-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.disabled-button {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $gray;
  cursor: not-allowed;
  color: white;
}
.add-button:disabled {
  display: flex;
  align-items: center;
  border: none;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $gray;
  cursor: not-allowed;
  color: white;
}
.add-button {
  display: flex;
  align-items: center;
  border: none;
  height: 4.5vh;
  // box-shadow: 1px 2px 3px 1px $very-light-gray;
  margin: 0 0.5rem 0 0;
  padding: 0.25rem 0.6rem;
  border-radius: 0.2rem;
  background-color: $dark-green;
  cursor: pointer;
  color: white;
  transition: all 0.3s;
}

.add-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.resNum {
  color: $dark-green;
  font-weight: bold;
}
.search-bar {
  height: 4.5vh;
  background-color: $off-white;
  box-shadow: 1px 1px 1px $very-light-gray;
  border: 1px solid $soft-gray;
  display: flex;
  align-items: center;
  padding: 2px;
  border-radius: 5px;
  margin-right: 0.5rem;
}
#update-input {
  border: 1px solid $very-light-gray;
  border-radius: 0.4rem;
  padding: 3px;
  min-height: 4.5vh;
  min-width: 14vw;
}
.number-input {
  background-color: $off-white;
  box-shadow: 1px 1px 1px $gray;
  border: 2px solid $light-orange-gray;
  border-radius: 5px;
  min-height: 4vh;
  margin-right: 1rem;
  margin-left: 0.5rem;
  width: 6vw;
}
#update-input:focus,
.number-input:focus {
  outline: 2px solid $lighter-green;
}
.loader {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
  filter: invert(99%);
}
.invert {
  filter: invert(99%);
}
.wide {
  width: 100%;
}
.name-cell-note-button {
  height: 1.5rem;
  cursor: pointer;
  // box-shadow: 1px 1px 1px 1px $very-light-gray;
  border: none;
  border-radius: 50%;
  padding: 0.2rem;
  margin-right: 0.5rem;
  background-color: $lighter-green;
  transition: all 0.3s;
}
.name-cell-note-button:hover,
.name-cell-edit-note-button:hover {
  transform: scale(1.03);
  box-shadow: 1px 2px 2px $very-light-gray;
}
.name-cell-edit-note-button {
  height: 1.5rem;
  cursor: pointer;
  border: none;
  border-radius: 50%;
  padding: 0.2rem;
  margin-right: 0.25rem;
  background-color: $dark-green;
  transition: all 0.3s;
}
.header {
  font-size: 18px;
  letter-spacing: 1px;
  margin-bottom: 0.4rem;
}
.list-section {
  z-index: 2;
  position: absolute;
  top: 8vh;
  left: 0;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $off-white;
  width: 16vw;
  max-height: 40vh;
  overflow: scroll;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 3px 1px $very-light-gray;

  &__title {
    font-size: 13px;
    font-weight: bold;
    display: flex;
    align-items: center;
    margin-left: 0.75rem;
    color: $base-gray;
    cursor: pointer;

    img {
      margin: 2px 0px 0px 3px;
      height: 0.75rem;
      filter: invert(70%);
    }
  }
}
.filter-section {
  position: absolute;
  top: 8vh;
  left: 0;
  z-index: 2;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  background-color: $off-white;
  width: 20vw;
  margin-right: 0.5rem;
  box-shadow: 1px 1px 3px 1px $very-light-gray;

  &__title {
    color: $dark-green;
    margin-left: 0.75rem;
    font-weight: bold;
    border-bottom: 2px solid $dark-green;
    padding-bottom: 2px;
  }

  &__filters {
    // background-color: $white-green;
    border-radius: 5px;
    width: 100%;
    margin-top: 1rem;
  }
}
.list-button {
  display: flex;
  align-items: center;
  height: 4.5vh;
  width: 100%;
  background-color: transparent;
  border: none;
  padding: 0.75rem;
  border-radius: 0.2rem;
  color: $mid-gray;
  cursor: pointer;
  font-size: 11px;
  font-weight: bold;
}
.list-button:hover {
  color: $dark-green;
  background-color: white;
}
.filter {
  color: #199e54;
  margin-left: 0.2rem;
}
.exit {
  padding-right: 0.5rem;
  height: 1rem;
  cursor: pointer;
}
.filter-option-button {
  padding: 0.25rem 0.5rem;
  border: none;
  background-color: $dark-green;
  color: white;
  border-radius: 3px;
  margin: 0.1rem;
  font-size: 10px;
  cursor: pointer;
}
.filter-option-section {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  max-height: 10vh;
  padding: 0.5rem;
  border-radius: 1px;
  width: 100%;
  background-color: $white-green;
}
.filter-title {
  padding-left: 0.7rem;
  padding-top: 0.5rem;
  margin-top: 0.5rem;
  width: 100%;
  border-radius: 2px;
  color: $base-gray;
  background-color: $white-green;
}
.centered {
  display: flex;
  align-items: center;
  justify-content: center;

  &__button {
    display: flex;
    align-items: center;
    background-color: $dark-green;
    border: none;
    margin-left: 0.5rem;
    padding: 0.25rem;
    border-radius: 0.2rem;
    cursor: pointer;
  }
}
.drop-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
}
.cancel {
  color: $darker-green;
  font-weight: bold;
  margin-right: 1rem;
  cursor: pointer;
}
.flex-end {
  width: 100%;
  padding: 2rem 0.25rem;
  display: flex;
  align-items: center;
  justify-content: flex-end;
}
</style>