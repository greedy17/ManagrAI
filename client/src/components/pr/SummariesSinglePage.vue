<template>
  <div ref="loadedContent" class="main-content">
    <!-- <div class="suggestions" v-if="!selectedSearch">
      <img class="invert-dark-blue" src="@/assets/images/lightbulb.svg" height="18px" alt="" />
    </div> -->
    <Modal v-if="contentModalOpen" class="regen-modal">
      <div :class="{ dim: contentLoading }" class="regen-container">
        <div class="regen-header">
          <div>
            <h4 class="regen-header-title">Generate Content</h4>
            <p class="regen-header-subtitle">Provide additional instructions</p>
          </div>
          <div @click="closeContentModal" class="pointer"><small>X</small></div>
        </div>

        <div class="regen-body padding">
          <textarea
            class="area-input-outline wider"
            v-model="contentInstructions"
            type="text"
            v-autoresize
            :disabled="contentLoading"
          />
        </div>

        <div class="regen-footer">
          <div></div>
          <div class="row">
            <button :disabled="contentLoading" @click="closeContentModal" class="cancel-button">
              Cancel
            </button>
            <button :disabled="contentLoading" @click="generateContent" class="save-button">
              <img
                v-if="contentLoading"
                style="margin-right: 8px"
                src="@/assets/images/loading.svg"
                class="rotate"
                height="12px"
                alt=""
              />
              {{ contentLoading ? 'submitting' : 'submit' }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <!-- paidModal -->
    <Modal v-if="paidModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="closePaidModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Upgrade to Pro</h3>
              <h5 class="regen-body-title">
                {{ upgradeMessage }}
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="closePaidModal"
            >
              Close
            </div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="successModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="closeSuccessModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Payment Successful!</h3>
              <h5 class="regen-body-title">
                If you have any questions, email us at support@mymanagr.com
              </h5>
            </div>
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="closeSuccessModal"
            >
              Close
            </div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="errorModal" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title"></h4>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="() => (errorModal = false)"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center">
              <h3 class="paid-title">Something went wrong</h3>
              <h5 class="regen-body-title">Please try again later.</h5>
            </div>
            <!-- <textarea v-autoresize v-model="newTemplate" class="regen-body-text" /> -->
          </div>
        </div>
        <div class="paid-footer">
          <!-- <div></div> -->
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="() => (errorModal = false)"
            >
              Close
            </div>
            <div class="save-button" @click="goToContact">Contact Us</div>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="notifyModalOpen" class="paid-modal">
      <div class="regen-container">
        <div class="paid-header">
          <div>
            <h4 class="regen-header-title">Email Alerts</h4>
            <p class="regen-header-subtitle">
              {{ !alertSet ? 'Select delivery time' : 'Preview your alert' }}
            </p>
          </div>
          <div class="pointer" @click="toggleNotifyModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div v-if="!alertSet">
              <label for="time-select">Delivery time:</label>
              <input
                id="time-select"
                style="width: 100%"
                class="area-input-outline"
                required
                @input="calculateDate(alertTIme)"
                type="time"
                v-model="alertTIme"
              />
              <small style="font-size: 12px">Recieve a daily email when there is new content</small>
            </div>

            <div class="paid-center" v-else>
              <p>Email Notifications enabled.</p>

              <div class="row">
                <button @click="toggleNotifyModal" class="secondary-button">Close</button>
                <button class="primary-button" @click="testEmailAlert">Send Preview</button>
              </div>
            </div>
          </div>
        </div>
        <div class="paid-footer">
          <div v-if="!alertSet" class="row">
            <button
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="toggleNotifyModal"
            >
              Cancel
            </button>
            <button
              @click="addEmailAlert"
              :disabled="savingAlert || !alertTIme"
              class="save-button"
            >
              <img
                v-if="savingAlert"
                class="rotate"
                height="12px"
                src="@/assets/images/loading.svg"
                alt=""
                style="margin-right: 8px"
              />Submit
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="detailModalOpen" class="regen-modal">
      <div :class="{ dim: contentLoading }" class="regen-container">
        <div class="regen-header">
          <div>
            <h4 class="regen-header-title">Details</h4>
            <p class="regen-header-subtitle">Details lorem ipsum</p>
          </div>
          <div @click="toggleDetailModaldetails" class="pointer"><small>X</small></div>
        </div>

        <div class="regen-body padding">
          <label style="font-size: 13px" for="detail-title">Title:</label>
          <input
            id="detail-title"
            style="width: 100%; margin-bottom: 1rem"
            class="area-input-outline"
            type="text"
            v-model="detailTitle"
          />

          <label style="font-size: 13px" for="detail-text">Text:</label>
          <textarea
            id="detail-text"
            class="area-input-outline wider"
            v-model="detialText"
            type="text"
            v-autoresize
            :disabled="contentLoading"
          />
        </div>

        <div class="regen-footer">
          <div></div>
          <div class="row">
            <button :disabled="contentLoading" @click="toggleDetailModal" class="cancel-button">
              Cancel
            </button>
            <button :disabled="contentLoading" class="save-button">
              <img
                v-if="contentLoading"
                style="margin-right: 8px"
                src="@/assets/images/loading.svg"
                class="rotate"
                height="12px"
                alt=""
              />
              {{ contentLoading ? 'saving' : 'save' }}
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Transition name="slide-left">
      <div v-if="selectedSearch && ShowReport" class="reports-width-height">
        <div class="reports-lip-container" @click="toggleReport">
          <div class="reports-lip">
            <img src="@/assets/images/rightarrow.svg" class="lip-img invert-dark-blue" />
          </div>
        </div>
        <Reports
          @toggle-report="toggleReport"
          @clear-clips="clearClips"
          @remove-clip="removeClip"
          @edit-clip="editClip"
          @add-clip="addClip"
          @set-added-clips="setAddedClips"
          :clips="allCategoryClips"
          :defaultSearch="newSearch"
        />
      </div>
    </Transition>

    <div @click="toggleReport" v-if="selectedSearch && !ShowReport" class="floating-action-bar">
      <div :class="{ 'added-clip': addedClip }" class="reports-lip-closed">
        <img
          v-if="!addedClip"
          src="@/assets/images/rightarrow.svg"
          class="lip-img invert-dark-blue"
        />
        <img v-else src="@/assets/images/add.svg" class="lip-img invert-dark-blue" />
      </div>

      <!-- <div class="slot-container">
        <div v-for="(clip, i) in allCategoryClips" :key="i">
          <img v-if="i < 5" :src="clip.image_url" class="small-photo" />
        </div>

        <div v-if="!allCategoryClips || allCategoryClips.length < 1" class="empty-slot"></div>
        <div v-if="!allCategoryClips || allCategoryClips.length < 2" class="empty-slot"></div>
        <div v-if="!allCategoryClips || allCategoryClips.length < 3" class="empty-slot"></div>
        <div v-if="!allCategoryClips || allCategoryClips.length < 4" class="empty-slot"></div>
        <div v-if="!allCategoryClips || allCategoryClips.length < 5" class="empty-slot"></div>
      </div>

      <div class="slot-count">
        <small>{{ allCategoryClips ? allCategoryClips.length : 0 }}/20</small>
      </div> -->
    </div>

    <div class="center column" :class="{ fullHeight: showingDropdown }" v-if="page === 'SUMMARIES'">
      <!-- <div v-if="!selectedSearch" class="switcher">
        <div
          @click="switchMainView('news')"
          :class="{ activeswitch: mainView === 'news' }"
          class="switch-item"
          id="news-tab"
        >
          <img src="@/assets/images/memo.svg" height="12px" alt="" />
          News
        </div>
        <div
          @click="switchMainView('social')"
          :class="{ activeswitch: mainView === 'social' }"
          class="switch-item"
          id="social-tab"
        >
          <img src="@/assets/images/comment.svg" height="12px" alt="" />
          Social
        </div>
        <div
          @click="switchMainView('website')"
          :class="{ activeswitch: mainView === 'website' }"
          class="switch-item"
          id="articles-tab"
        >
          <img src="@/assets/images/globe.svg" height="16px" alt="" />
          Articles
        </div>
      </div> -->

      <div class="no-content">
        <div :class="{ 'neg-mar-btm': mainView === 'website' }" class="title-row main-header">
          <div style="width: 50%; padding: 0 32px">
            <h2 style="margin-bottom: 0">Create report</h2>

            <!-- <div class="row">
              
              <img
                class="white-img"
                v-if="!showingViews"
                src="@/assets/images/downArrow.svg"
                height="14px"
                alt=""
              />
              <img
                class="rotate-img white-img"
                v-else
                src="@/assets/images/downArrow.svg"
                height="14px"
                alt=""
              />
            </div> -->

            <p style="margin-top: 8px" class="typed">
              {{
                mainView === 'social'
                  ? 'Instantly search through X (formally Twitter).'
                  : mainView === 'website'
                  ? 'Instantly summarize a news article.'
                  : 'Generate an AI report based on news coverage.'
              }}
            </p>
          </div>

          <div class="news-column">
            <div
              v-if="mainView !== 'website'"
              style="margin-bottom: 30px; padding: 0 16px"
              class="input-container"
              id="prompt-search"
              v-clickOutsideMenu
            >
              <div style="margin-right: -8px" class="input-row">
                <div class="main-text">Instructions</div>
                <textarea
                  @keyup.enter="generateNewSearch(false)"
                  id="search-input"
                  class="area-input text-area-input"
                  placeholder="Type instructions..."
                  @focus="showDropdown"
                  autocomplete="off"
                  v-model="newSearch"
                  v-autoresize
                  :disabled="loading || summaryLoading"
                />

                <div class="switcher">
                  <div
                    @click="switchMainView('news')"
                    :class="{ activeswitch: mainView === 'news' }"
                    class="switch-item"
                    id="news-tab"
                  >
                    News
                  </div>
                  <!-- <div
                    @click="switchMainView('social')"
                    :class="{ activeswitch: mainView === 'social' }"
                    class="switch-item"
                    id="social-tab"
                  >
                    Social
                  </div> -->
                  <div
                    @click="switchMainView('website')"
                    :class="{ activeswitch: mainView === 'website' }"
                    class="switch-item"
                    id="articles-tab"
                  >
                    Article
                  </div>
                </div>

                <button
                  @click="generateNewSearch(false)"
                  :disabled="!newSearch || loading || summaryLoading"
                  style="
                    margin: 0;
                    margin-left: 8px;
                    border: none !important;
                    background-color: transparent;
                  "
                  id="generate-summary"
                >
                  <img
                    v-if="!newSearch || loading || summaryLoading"
                    style="margin: 0"
                    src="@/assets/images/paper-plane-top.svg"
                    height="14px"
                    alt=""
                    class="faded"
                  />

                  <img
                    v-else
                    style="margin: 0"
                    src="@/assets/images/paper-plane-full.svg"
                    height="13px"
                    alt=""
                    class="grow filtered-blue"
                  />
                </button>
              </div>

              <div v-if="showingDropdown" class="dropdown">
                <small style="padding-top: 8px" class="gray-text">Date Range</small>
                <div style="width: 100%; margin-top: 8px">
                  <input class="area-input-smallest" type="date" v-model="dateStart" />
                  -
                  <input class="area-input-smallest" type="date" v-model="dateEnd" />
                </div>
                <small style="padding-top: 8px" class="gray-text">Popular Searches</small>
                <div
                  @click="addSuggestion(suggestion)"
                  class="dropdown-item"
                  v-for="(suggestion, i) in filteredPromptSuggestions"
                  :key="i"
                >
                  <p>
                    {{ suggestion }}
                  </p>
                </div>
              </div>
            </div>

            <div
              v-else-if="mainView === 'website'"
              style="margin-bottom: 30px"
              class="input-container"
            >
              <div style="margin-right: -8px" class="input-row">
                <div class="main-text">Article</div>
                <input
                  @keyup.enter="uploadArticle"
                  class="area-input-small"
                  placeholder="Paste article url..."
                  v-model="uploadLink"
                />
                <div class="switcher">
                  <div
                    @click="switchMainView('news')"
                    :class="{ activeswitch: mainView === 'news' }"
                    class="switch-item"
                    id="news-tab"
                  >
                    News
                  </div>
                  <!-- <div
                    @click="switchMainView('social')"
                    :class="{ activeswitch: mainView === 'social' }"
                    class="switch-item"
                    id="social-tab"
                  >
                    Social
                  </div> -->
                  <div
                    @click="switchMainView('website')"
                    :class="{ activeswitch: mainView === 'website' }"
                    class="switch-item"
                    id="articles-tab"
                  >
                    Article
                  </div>
                </div>

                <button
                  @click="uploadArticle"
                  :disabled="!uploadLink || clipLoading"
                  style="
                    margin: 0;
                    margin-left: 8px;

                    border: none !important;
                    background-color: transparent;
                  "
                  id="generate-summary"
                >
                  <img
                    v-if="!uploadLink || clipLoading"
                    style="margin: 0"
                    src="@/assets/images/paper-plane-top.svg"
                    height="14px"
                    alt=""
                    class="faded"
                  />

                  <img
                    v-else
                    style="margin: 0"
                    src="@/assets/images/paper-plane-full.svg"
                    height="13px"
                    alt=""
                    class="grow filtered-blue"
                  />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="loaded-content">
        <div class="summaries-container">
          <Transition name="slide-fade">
            <div v-if="showUpdateBanner" class="templates">
              <p>Success!</p>
            </div>
          </Transition>
          <Transition name="slide-fade">
            <div v-if="showNotifyBanner" class="templates">
              <p>Success!</p>
            </div>
          </Transition>
          <div class="content-width">
            <div class="news-container">
              <div class="title-container">
                <div class="space-between">
                  <div v-if="loading" style="margin-left: -12px" class="row">
                    <div class="loading">
                      <div class="dot"></div>
                      <div class="dot"></div>
                      <div class="dot"></div>
                    </div>
                  </div>

                  <p style="margin: 16px 0" v-else-if="!selectedSearch" class="sub-text">
                    Your report will appear below.
                  </p>
                  <p
                    v-else-if="selectedSearch && mainView !== 'website'"
                    class="sub-text ellipsis-text"
                    style="margin: 16px 0"
                  >
                    AI-generated boolean: <span :title="booleanString">{{ booleanString }}</span>
                  </p>
                  <p v-else style="margin: 16px 0" class="sub-text">Article Report</p>

                  <p v-if="selectedSearch" style="margin-right: 4px; font-size: 14px">
                    {{
                      mainView === 'news'
                        ? `${filteredArticles.length} News Clips`
                        : mainView === 'website'
                        ? '1 Article'
                        : `${tweets.length} Tweets`
                    }}
                  </p>

                  <!-- <p v-else style="margin-right: 4px; font-size: 14px">
                    {{
                      mainView === 'news' ? `News` : mainView === 'website' ? 'Article' : `Tweets`
                    }}
                  </p> -->
                </div>

                <div
                  v-if="
                    !selectedSearch ||
                    !(
                      (filteredArticles && filteredArticles.length) ||
                      tweets.length ||
                      addedArticles.length
                    )
                  "
                  class="space-between"
                  style="position: relative"
                >
                  <div class="wrapper">
                    <button disabled style="margin-left: 0" class="primary-button">Save</button>
                    <div style="margin-left: -8px" class="tooltip tooltip-wide full">
                      Generate report first
                    </div>
                  </div>

                  <div v-if="mainView !== 'website'">
                    <div
                      style="margin-right: 0; right: 80px"
                      class="wrapper absolute-right-bottom circle-border white-bg dim"
                    >
                      <img
                        style="cursor: not-allowed"
                        class="right-mar img-highlight"
                        src="@/assets/images/bell.svg"
                        height="14px"
                        alt=""
                      />
                      <div style="margin-left: -22px" class="tooltip tooltip-wide full">
                        Generate report first
                      </div>
                    </div>

                    <div
                      style="margin-right: 0; right: 40px"
                      class="wrapper absolute-right-bottom circle-border white-bg dim"
                    >
                      <img
                        style="cursor: not-allowed"
                        class="right-mar img-highlight"
                        src="@/assets/images/email-round.svg"
                        height="14px"
                        alt=""
                      />
                      <div style="margin-left: -22px" class="tooltip tooltip-wide full">
                        Generate report first
                      </div>
                    </div>

                    <div class="wrapper absolute-right-bottom circle-border white-bg dim">
                      <img
                        style="cursor: not-allowed"
                        class="right-mar img-highlight"
                        src="@/assets/images/clipboard.svg"
                        height="14px"
                        alt=""
                      />
                      <div style="margin-left: -22px" class="tooltip tooltip-wide full">
                        Generate report first
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div style="width: 100%" v-if="selectedSearch">
                <div v-if="summary && summarizing" class="title-bar">
                  <div v-if="!showSaveName" class="row-container">
                    <div class="row">
                      <!-- @click="openRegenModal" -->
                      <button
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                        @click="summarizing = false"
                        class="secondary-button"
                      >
                        <!-- {{
                          (filteredArticles && filteredArticles.length) || mainView === 'website'
                            ? 'New'
                            : tweets.length
                            ? 'New'
                            : 'New Search'
                        }} -->

                        Chat
                      </button>

                      <button
                        @click="toggleSaveName"
                        v-if="
                          !savedSearch &&
                          ((filteredArticles && filteredArticles.length) || tweets.length)
                        "
                        :disabled="
                          articleSummaryLoading ||
                          loading ||
                          summaryLoading ||
                          savingSearch ||
                          savedSearch ||
                          mainView === 'website'
                        "
                        style="margin-left: -2px"
                        class="primary-button"
                      >
                        <img
                          v-if="savingSearch"
                          class="rotate"
                          height="12px"
                          src="@/assets/images/loading.svg"
                          alt=""
                        />
                        {{ savingSearch ? 'Saving' : 'Save' }}
                      </button>
                    </div>
                  </div>

                  <div v-else class="row">
                    <input
                      autofocus
                      class="area-input-outline"
                      placeholder="Name your search"
                      v-model="searchName"
                    />

                    <button @click="toggleSaveName" class="secondary-button">Cancel</button>

                    <button
                      style="margin-left: -2px"
                      @click="createSearch"
                      :disabled="
                        articleSummaryLoading ||
                        loading ||
                        summaryLoading ||
                        savingSearch ||
                        searchSaved
                      "
                      class="primary-button"
                    >
                      Save
                    </button>
                  </div>

                  <!-- <div v-if="mainView === 'website' && addedArticles.length === 1" class="relative">
                    <div
                      @click="toggleGenerateDropdown"
                      class="row pointer dropdownBorder gen-content-button"
                    >
                      Generate Content
                      <img
                        v-if="!showGenerateDropdown"
                        src="@/assets/images/downArrow.svg"
                        class="inverted"
                        height="14px"
                        alt=""
                      />
                      <img
                        class="rotate-img inverted"
                        v-else
                        src="@/assets/images/downArrow.svg"
                        height="14px"
                        alt=""
                      />
                    </div>

                    <div v-if="showGenerateDropdown" class="search-dropdown">
                      <div class="searches-container">
                        <div
                          class="row relative"
                          v-for="(option, i) in articleGenerateOptions"
                          :key="option.value"
                        >
                          <p @click="selectArticleOption(addedArticles[0].link, option.value, i)">
                            {{ option.name }}
                          </p>

                          <img
                            v-show="contentLoading && optionIndex === i"
                            src="@/assets/images/loading.svg"
                            class="rotate"
                            height="12px"
                            alt=""
                          />
                        </div>
                      </div>
                    </div>
                  </div> -->
                </div>

                <div
                  :class="{ bottommargin: summary && !summaryLoading }"
                  v-else-if="
                    !summarizing &&
                    ((filteredArticles && filteredArticles.length) ||
                      (tweets && tweets.length) ||
                      addedArticles.length)
                  "
                  style="width: 100%"
                >
                  <div v-if="showGenerateDropdown" class="content-dropdown">
                    <div class="searches-container">
                      <div
                        class="row relative"
                        v-for="(option, i) in generateOptions"
                        :key="option.value"
                      >
                        <p @click="setContentInstructions(option.name, option.value)">
                          {{ option.name }}
                        </p>

                        <img
                          v-show="contentLoading && optionIndex === i"
                          src="@/assets/images/loading.svg"
                          class="rotate"
                          height="12px"
                          alt=""
                        />
                      </div>
                    </div>
                  </div>

                  <div v-if="!summaryLoading">
                    <div
                      style="
                        margin: 1rem 0 0 0;
                        width: 100%;
                        padding-top: 0;
                        padding-bottom: 0;
                        border-radius: 28px;
                      "
                      id="instructions"
                      class="input-container"
                      v-clickOutsidePromptMenu
                      v-if="showSummaryInstructions"
                    >
                      <div style="padding-top: 0" class="input-row">
                        <!-- @click="toggleGenerateDropdown" -->
                        <div class="main-text-img">
                          <img src="@/assets/images/comment.svg" height="16px" alt="" />
                          <!-- <p>Chat</p> -->
                          <!-- <img
                            v-if="!showGenerateDropdown"
                            src="@/assets/images/downArrow.svg"
                            class="inverted"
                            height="14px"
                            alt=""
                          />
                          <img
                            class="rotate-img inverted"
                            v-else
                            src="@/assets/images/downArrow.svg"
                            height="14px"
                            alt=""
                          /> -->
                        </div>
                        <!-- v-if="showSummaryInput" -->
                        <!-- @focus="showPromptDropdown" -->
                        <textarea
                          style="margin: 0"
                          class="area-input text-area-input"
                          id="instructions-text-area"
                          placeholder="Ask me anything about this coverage..."
                          v-model="newTemplate"
                          v-autoresize
                        />

                        <!-- <textarea
                          v-else
                          style="margin: 0"
                          class="area-input text-area-input"
                          id="instructions-text-area"
                          :placeholder="`Provide instructions for ${contentType}...`"
                          v-model="contentInstructions"
                          v-autoresize
                        /> -->

                        <button
                          @click="summarizing = true"
                          v-if="summary"
                          class="secondary-button"
                          style="margin-right: 0"
                        >
                          Cancel
                        </button>

                        <button
                          @click="getSummary(filteredArticles, newTemplate)"
                          v-if="mainView === 'news'"
                          :disabled="!newTemplate"
                          style="
                            margin: 0;
                            margin-left: 8px;
                            border: none !important;
                            background-color: transparent;
                          "
                        >
                          <img
                            v-if="!newTemplate"
                            style="margin: 0"
                            src="@/assets/images/paper-plane-top.svg"
                            height="14px"
                            alt=""
                            class="faded"
                          />

                          <img
                            v-else
                            style="margin: 0"
                            src="@/assets/images/paper-plane-full.svg"
                            height="13px"
                            alt=""
                            class="grow filtered-blue"
                          />
                        </button>

                        <!-- <button
                          @click="getTweetSummary(filteredArticles, newTemplate)"
                          v-else-if="mainView === 'social'"
                          style="
                            margin: 0;
                            margin-left: 8px;
                            border: none !important;
                            background-color: transparent;
                          "
                        >
                          <img src="@/assets/images/sparkle.svg" height="14px" alt="" />
                        </button> -->
                        <button
                          @click="getSourceSummary"
                          :disabled="!newTemplate"
                          v-else
                          style="
                            margin: 0;
                            margin-left: 8px;
                            border: none !important;
                            background-color: transparent;
                          "
                        >
                          <img
                            v-if="!newTemplate"
                            style="margin: 0"
                            src="@/assets/images/paper-plane-top.svg"
                            height="14px"
                            alt=""
                            class="faded"
                          />

                          <img
                            v-else
                            style="margin: 0"
                            src="@/assets/images/paper-plane-full.svg"
                            height="13px"
                            alt=""
                            class="grow filtered-blue"
                          />
                        </button>
                      </div>

                      <div v-if="showingPromptDropdown" class="dropdown">
                        <div style="padding-top: 4px; padding-bottom: 4px">
                          <small class="gray-text">Popular Prompts</small>
                        </div>

                        <div
                          class="dropdown-item"
                          v-for="(suggestion, i) in filteredPromptSuggestions"
                          :key="i"
                          @click="addPromptSuggestion(suggestion)"
                        >
                          <p>
                            {{ suggestion }}
                          </p>
                        </div>
                      </div>
                    </div>

                    <div class="space-between relative" v-else>
                      <button
                        @click="showSummaryInstructions = true"
                        style="margin-left: 0"
                        class="primary-button"
                      >
                        <img src="@/assets/images/sparkle.svg" height="14px" alt="" />Generate
                        Report
                      </button>

                      <div v-if="mainView !== 'website'">
                        <div
                          style="margin-right: 0; right: 80px"
                          class="wrapper absolute-right-bottom circle-border white-bg dim"
                        >
                          <img
                            style="cursor: not-allowed"
                            class="right-mar img-highlight"
                            src="@/assets/images/bell.svg"
                            height="14px"
                            alt=""
                          />
                          <div style="margin-left: -22px" class="tooltip tooltip-wide full">
                            Generate report first
                          </div>
                        </div>

                        <div
                          style="margin-right: 0; right: 40px"
                          class="wrapper absolute-right-bottom circle-border white-bg dim"
                        >
                          <img
                            style="cursor: not-allowed"
                            class="right-mar img-highlight"
                            src="@/assets/images/email-round.svg"
                            height="14px"
                            alt=""
                          />
                          <div style="margin-left: -22px" class="tooltip tooltip-wide full">
                            Generate report first
                          </div>
                        </div>

                        <div class="wrapper absolute-right-bottom circle-border white-bg dim">
                          <img
                            style="cursor: not-allowed"
                            class="right-mar img-highlight"
                            src="@/assets/images/clipboard.svg"
                            height="14px"
                            alt=""
                          />
                          <div style="margin-left: -22px" class="tooltip tooltip-wide full">
                            Generate report first
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div style="margin: 1.5rem 0 0 0" class="loader-bg" v-else>
                    <div class="summary-preview-skeleton shimmer">
                      <div class="content">
                        <div class="meta-wide"></div>
                        <div class="meta-shorter"></div>
                        <div class="meta-shortest"></div>
                      </div>
                    </div>
                  </div>
                </div>

                <div v-if="summary" style="width: 100%" class="relative">
                  <div
                    @mouseenter="changeEmailText"
                    @mouseleave="defaultEmailText"
                    @click="toggleNotifyModal"
                    class="wrapper absolute-right circle-border white-bg"
                    style="margin-right: 0; right: 88px"
                    :disabled="sentSummaryEmail"
                    v-if="mainView === 'news' && summarizing && !notifiedList.includes(searchId)"
                  >
                    <img
                      height="14px"
                      src="@/assets/images/bell.svg"
                      alt=""
                      class="filter-green img-highlight"
                      :class="{ dim: !(searchSaved || savedSearch) }"
                    />
                    <div
                      class="tooltip"
                      style="margin-left: -22px"
                      :class="{ 'tooltip-wide': !(searchSaved || savedSearch) }"
                    >
                      {{ searchSaved || savedSearch ? emailText : 'Save search to enable alerts' }}
                    </div>
                  </div>

                  <div
                    @click="removeEmailAlert"
                    class="wrapper absolute-right circle-border white-bg"
                    style="margin-right: 0; right: 88px"
                    v-else-if="
                      mainView === 'news' &&
                      summarizing &&
                      (searchSaved || savedSearch) &&
                      notifiedList.includes(searchId)
                    "
                  >
                    <img
                      height="14px"
                      src="@/assets/images/bell-slash.svg"
                      alt=""
                      class="img-highlight"
                    />
                    <div class="tooltip" style="margin-left: -22px">Disable</div>
                  </div>

                  <div
                    @click="sendSummaryEmail"
                    class="wrapper absolute-right circle-border white-bg"
                    style="margin-right: 0; right: 48px"
                    :disabled="sentSummaryEmail"
                    v-if="mainView !== 'social' && mainView !== 'website' && summarizing"
                  >
                    <img
                      v-if="sendingSummaryEmail"
                      class="rotate img-highlight"
                      height="14px"
                      src="@/assets/images/loading.svg"
                      alt=""
                    />
                    <img
                      v-else
                      height="14px"
                      src="@/assets/images/email-round.svg"
                      alt=""
                      class="filter-green img-highlight"
                    />
                    <!-- <span class="summary-email-span">{{ sendSummaryEmailText }}</span> -->
                    <div
                      v-if="sendSummaryEmailText !== 'Sent!'"
                      style="margin-left: -22px"
                      class="tooltip"
                    >
                      Send Email
                    </div>
                  </div>

                  <div
                    @click="copyText"
                    class="wrapper absolute-right circle-border white-bg"
                    v-if="summarizing"
                  >
                    <img
                      style="cursor: pointer"
                      class="right-mar img-highlight"
                      src="@/assets/images/clipboard.svg"
                      height="14px"
                      alt=""
                    />
                    <div style="margin-left: -22px" class="tooltip">{{ copyTip }}</div>
                  </div>

                  <pre
                    style="
                      margin-top: -4px;
                      padding-top: 16px;
                      border-top: 1px solid rgba(0, 0, 0, 0.1);
                    "
                    class="pre-text"
                    v-html="summary"
                  ></pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div ref="topDivider"></div>

        <!-- <div
          ref="topDivider"
          v-if="
            ((filteredArticles && filteredArticles.length) ||
              (tweets && tweets.length) ||
              addedArticles.length) &&
            !loading
          "
          class="divider"
        >
          <p class="divider-text">
            {{
              mainView === 'news'
                ? `${filteredArticles.length} News Clips`
                : mainView === 'website'
                ? 'Articles'
                : `${tweets.length} Tweets`
            }}
          </p>
        </div> -->

        <div style="background-color: white" class="loaded-content" v-if="loading">
          <div style="width: 50%">
            <div class="article-preview-skeleton shimmer">
              <div class="content">
                <div class="title"></div>
                <div class="meta"></div>
                <div class="excerpt"></div>
                <div class="skeleton-footer"></div>
              </div>
              <div class="thumbnail"></div>
            </div>
            <div class="article-preview-skeleton shimmer">
              <div class="content">
                <div class="title"></div>
                <div class="meta"></div>
                <div class="excerpt"></div>
                <div class="skeleton-footer"></div>
              </div>
              <div class="thumbnail"></div>
            </div>
            <div class="article-preview-skeleton shimmer">
              <div class="content">
                <div class="title"></div>
                <div class="meta"></div>
                <div class="excerpt"></div>
                <div class="skeleton-footer"></div>
              </div>
              <div class="thumbnail"></div>
            </div>
          </div>
        </div>

        <div v-else class="clips-container">
          <div class="content-width" v-if="mainView === 'social' && tweets.length">
            <div class="news-container-med" v-for="(tweet, i) in tweets" :key="i">
              <div style="padding-left: 8px" class="news-card-medium">
                <div class="attachment-header-container">
                  <div>
                    <header>
                      <div class="card-row-med">
                        <img :src="tweet.user.profile_image_url" />
                        <h1 @click="openTweet(tweet.user.username, tweet.id)" class="article-title">
                          {{ tweet.user.name }}
                        </h1>
                        <svg
                          v-if="tweet.user.verified"
                          width="16"
                          height="16"
                          viewBox="0 0 22 22"
                          aria-label="Verified account"
                          role="img"
                          class="twitter-blue"
                          data-testid="icon-verified"
                        >
                          <g>
                            <path
                              d="M20.396 11c-.018-.646-.215-1.275-.57-1.816-.354-.54-.852-.972-1.438-1.246.223-.607.27-1.264.14-1.897-.131-.634-.437-1.218-.882-1.687-.47-.445-1.053-.75-1.687-.882-.633-.13-1.29-.083-1.897.14-.273-.587-.704-1.086-1.245-1.44S11.647 1.62 11 1.604c-.646.017-1.273.213-1.813.568s-.969.854-1.24 1.44c-.608-.223-1.267-.272-1.902-.14-.635.13-1.22.436-1.69.882-.445.47-.749 1.055-.878 1.688-.13.633-.08 1.29.144 1.896-.587.274-1.087.705-1.443 1.245-.356.54-.555 1.17-.574 1.817.02.647.218 1.276.574 1.817.356.54.856.972 1.443 1.245-.224.606-.274 1.263-.144 1.896.13.634.433 1.218.877 1.688.47.443 1.054.747 1.687.878.633.132 1.29.084 1.897-.136.274.586.705 1.084 1.246 1.439.54.354 1.17.551 1.816.569.647-.016 1.276-.213 1.817-.567s.972-.854 1.245-1.44c.604.239 1.266.296 1.903.164.636-.132 1.22-.447 1.68-.907.46-.46.776-1.044.908-1.681s.075-1.299-.165-1.903c.586-.274 1.084-.705 1.439-1.246.354-.54.551-1.17.569-1.816zM9.662 14.85l-3.429-3.428 1.293-1.302 2.072 2.072 4.4-4.794 1.347 1.246z"
                            ></path>
                          </g>
                        </svg>
                      </div>
                    </header>

                    <p class="article-preview">{{ tweet.text }}</p>
                  </div>
                  <div v-if="tweet.attachments" class="tweet-attachement">
                    <div
                      style="margin-bottom: 16px"
                      v-for="media in tweetMedia"
                      :key="media.media_key"
                    >
                      <div v-if="media.media_key === tweet.attachments.media_keys[0]">
                        <img
                          v-if="media.type === 'photo'"
                          :src="media.url"
                          class="cover-photo-no-l-margin"
                          alt=""
                        />

                        <video
                          style="margin-top: 1rem"
                          v-else-if="media.type === 'video'"
                          width="400"
                          height="200"
                          controls
                        >
                          <source :src="media.variants[1].url" type="video/mp4" />
                        </video>

                        <video
                          style="margin-top: 1rem"
                          v-else-if="media.type === 'animated_gif'"
                          width="400"
                          autoplay
                          loop
                          muted
                          playsinline
                        >
                          <source :src="media.variants[0].url" type="video/mp4" />
                        </video>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="card-footer">
                  <div class="author-time">
                    <span class="author">{{ '@' + tweet.user.username }}</span>
                    <span class="divier-dot">.</span>
                    <small class="bold-text"
                      >{{ formatNumber(tweet.user.public_metrics.followers_count) }}
                      <span>Followers</span>
                    </small>
                    <span class="divier-dot">.</span>
                    <span class="off-gray time">{{
                      getTimeDifferenceInMinutes(tweet.created_at)
                    }}</span>
                  </div>
                  <button
                    :disabled="clipTitles.includes(tweet.id)"
                    class="tertiary-button"
                    @click="addClip(tweet)"
                  >
                    <img height="10px" src="@/assets/images/share.svg" alt="" />

                    {{ clipTitles.includes(tweet.id) ? 'Shared' : 'Share' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="content-width" v-else-if="mainView === 'social' && tweetError">
            <div class="news-container">
              <div class="no-results">
                <p>{{ tweetError }}</p>
              </div>
            </div>
          </div>
          <div v-else-if="mainView === 'news'" class="content-width">
            <div v-for="article in filteredArticles" :key="article.id" class="news-container">
              <div class="news-card" @click="selectArticle(article)">
                <header>
                  <div class="card-col">
                    <div class="card-top-left">
                      <!-- <img :src="article.icon" /> -->
                      <span>{{ article.source.name }}</span>
                    </div>
                    <h1 class="article-title" @click="goToArticle(article.link)">
                      {{ article.title }}
                    </h1>
                    <p class="article-preview">
                      {{ article.description }}
                    </p>
                  </div>

                  <!-- <div @click="goToArticle(article.link)"> -->
                  <img
                    @click="goToArticle(article.link)"
                    :src="article.image_url"
                    class="cover-photo"
                  />
                  <!-- </div> -->
                </header>

                <div class="card-footer">
                  <div class="author-time">
                    <span class="author">{{ article.author }}</span>
                    <span class="divier-dot">.</span>
                    <span class="off-gray time">{{
                      getTimeDifferenceInMinutes(article.publish_date)
                    }}</span>
                    <span class="divier-dot">.</span>
                  </div>
                  <div class="footer-icon-container">
                    <button
                      :disabled="clipTitles.includes(article.title)"
                      class="tertiary-button"
                      @click="addClip(article)"
                    >
                      <img height="10px" src="@/assets/images/share.svg" alt="" />

                      {{ clipTitles.includes(article.title) ? 'Shared' : 'Share' }}
                    </button>

                    <div v-if="mainView === 'website' && addedArticles.length === 1"></div>
                    <div v-else>
                      <button
                        v-if="!article.summary"
                        @click="getArticleSummary(article.link)"
                        class="tertiary-button summarize-button"
                        style="margin: 0"
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                      >
                        <img
                          v-if="articleSummaryLoading && loadingUrl === article.link"
                          class="rotate"
                          height="14px"
                          src="@/assets/images/loading.svg"
                          alt=""
                        />
                        <img v-else src="@/assets/images/sparkles-thin.svg" height="14px" alt="" />
                        {{
                          articleSummaryLoading && loadingUrl === article.link
                            ? 'Summarizing'
                            : 'Summarize'
                        }}
                      </button>
                      <img
                        v-else
                        src="@/assets/images/sparkle.svg"
                        class="right-arrow-footer blue-icon"
                      />
                    </div>
                  </div>
                </div>
                <div v-if="mainView === 'website' && addedArticles.length === 1"></div>
                <div v-else-if="article.summary">
                  <div class="blue-bg display-flex">
                    <pre v-html="article.summary" class="pre-text"></pre>
                    <div
                      @click="copyArticleSummary(article.summary)"
                      class="wrapper article-copy-container circle-border"
                      style="padding: 12px 6px; border: 0.5px solid #2f4656"
                    >
                      <img
                        style="cursor: pointer"
                        class="img-highlight"
                        src="@/assets/images/clipboard.svg"
                        height="12px"
                        alt=""
                      />
                      <div style="margin-left: -22px" class="tooltip">{{ copyTip }}</div>
                    </div>
                  </div>

                  <div class="regenerate-article">
                    <div v-if="!showArticleRegenerate" class="row">
                      <button
                        @click="toggleArticleRegenerate"
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                        class="tertiary-button"
                      >
                        Regenerate
                      </button>

                      <div class="relative">
                        <div
                          @click="toggleArticleGenerateDropdown"
                          class="row pointer nav-text dropdownBorder"
                        >
                          Generate Content
                          <img
                            v-if="!showArticleGenerateDropdown && !contentLoading"
                            src="@/assets/images/downArrow.svg"
                            class="inverted"
                            height="14px"
                            alt=""
                          />
                          <img
                            class="rotate-img inverted"
                            v-else-if="!contentLoading"
                            src="@/assets/images/downArrow.svg"
                            height="14px"
                            alt=""
                          />
                        </div>

                        <div v-if="showArticleGenerateDropdown" class="search-dropdown">
                          <div class="searches-container">
                            <div
                              class="row relative"
                              v-for="(option, i) in articleGenerateOptions"
                              :key="option.value"
                            >
                              <p @click="selectArticleOption(article.link, option.value, i)">
                                {{ option.name }}
                              </p>

                              <img
                                v-show="contentLoading && optionIndex === i"
                                src="@/assets/images/loading.svg"
                                class="rotate"
                                height="12px"
                                alt=""
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="full-width" v-else>
                      <textarea
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                        autofocus
                        class="area-input-outline wider"
                        placeholder="Provide additional instructions"
                        v-autoresize
                        v-model="articleInstructions"
                      />

                      <div class="row">
                        <button @click="toggleArticleRegenerate" class="secondary-button">
                          Cancel
                        </button>

                        <button
                          @click="
                            regenerateArticleSummary(
                              article.link,
                              article.summary,
                              articleInstructions,
                            )
                          "
                          :disabled="
                            articleSummaryLoading || loading || summaryLoading || savingSearch
                          "
                          class="primary-button"
                        >
                          <img
                            v-if="articleSummaryLoading && loadingUrl === article.link"
                            class="rotate"
                            height="14px"
                            src="@/assets/images/loading.svg"
                            alt=""
                          />
                          {{
                            articleSummaryLoading && loadingUrl === article.link
                              ? 'Submitting'
                              : 'Submit'
                          }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="mainView === 'website'" class="content-width">
            <div v-for="(article, i) in addedArticles" :key="i" class="news-container">
              <div class="news-card" @click="selectArticle(article)">
                <header>
                  <div class="card-col">
                    <div class="card-top-left">
                      <!-- <img :src="article.icon" /> -->
                      <span>{{ article.source }}</span>
                    </div>
                    <h1 class="article-title" @click="goToArticle(article.link)">
                      {{ article.title ? article.title : 'Error uploading article' }}
                    </h1>
                    <p class="article-preview">
                      {{
                        article.description
                          ? article.description
                          : 'Link broken, summary may be unavailable'
                      }}
                    </p>
                  </div>

                  <!-- <div @click="goToArticle(article.link)"> -->
                  <img
                    @click="goToArticle(article.link)"
                    :src="article.image_url"
                    class="cover-photo"
                  />
                  <!-- </div> -->
                </header>

                <div class="card-footer">
                  <div class="author-time">
                    <span class="author">{{ article.author }}</span>
                    <span class="divier-dot">.</span>
                    <span class="off-gray time">{{
                      getTimeDifferenceInMinutes(article.publish_date)
                    }}</span>
                    <span class="divier-dot">.</span>
                  </div>
                  <div class="footer-icon-container">
                    <!-- <button
                      :disabled="clipTitles.includes(article.title)"
                      class="tertiary-button"
                      @click="addClip(article)"
                    >
                      <img height="10px" src="@/assets/images/share.svg" alt="" />

                      {{ clipTitles.includes(article.title) ? 'Shared' : 'Share' }}
                    </button> -->

                    <div v-if="mainView === 'website' && addedArticles.length === 1"></div>
                    <div v-else>
                      <button
                        v-if="!article.summary"
                        @click="getArticleSummary(article.link)"
                        class="tertiary-button summarize-button"
                        style="margin: 0"
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                      >
                        <img
                          v-if="articleSummaryLoading && loadingUrl === article.link"
                          class="rotate"
                          height="14px"
                          src="@/assets/images/loading.svg"
                          alt=""
                        />
                        <img v-else src="@/assets/images/sparkles-thin.svg" height="14px" alt="" />
                        {{
                          articleSummaryLoading && loadingUrl === article.link
                            ? 'Summarizing'
                            : 'Summarize'
                        }}
                      </button>
                      <img
                        v-else
                        src="@/assets/images/sparkle.svg"
                        class="right-arrow-footer blue-icon"
                      />
                    </div>
                  </div>
                </div>
                <div v-if="mainView === 'website' && addedArticles.length === 1"></div>
                <div v-else-if="article.summary">
                  <div class="blue-bg display-flex">
                    <pre v-html="article.summary" class="pre-text"></pre>
                    <div
                      @click="copyArticleSummary(article.summary)"
                      class="wrapper article-copy-container circle-border"
                      style="padding: 12px 6px; border: 0.5px solid #2f4656"
                    >
                      <img
                        style="cursor: pointer"
                        class="img-highlight"
                        src="@/assets/images/clipboard.svg"
                        height="12px"
                        alt=""
                      />
                      <div style="margin-left: -22px" class="tooltip">{{ copyTip }}</div>
                    </div>
                  </div>

                  <div class="regenerate-article">
                    <div v-if="!showArticleRegenerate" class="row">
                      <button
                        @click="toggleArticleRegenerate"
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                        class="tertiary-button"
                      >
                        Regenerate
                      </button>

                      <div class="relative">
                        <div
                          @click="toggleArticleGenerateDropdown"
                          class="row pointer nav-text dropdownBorder"
                        >
                          Generate Content
                          <img
                            v-if="!showArticleGenerateDropdown"
                            src="@/assets/images/downArrow.svg"
                            class="inverted"
                            height="14px"
                            alt=""
                          />
                          <img
                            class="rotate-img inverted"
                            v-else
                            src="@/assets/images/downArrow.svg"
                            height="14px"
                            alt=""
                          />
                        </div>

                        <div v-if="showArticleGenerateDropdown" class="search-dropdown">
                          <div class="searches-container">
                            <div
                              class="row relative"
                              v-for="(option, i) in articleGenerateOptions"
                              :key="option.value"
                            >
                              <p @click="selectArticleOption(article.link, option.value, i)">
                                {{ option.name }}
                              </p>

                              <img
                                v-show="contentLoading && optionIndex === i"
                                src="@/assets/images/loading.svg"
                                class="rotate"
                                height="12px"
                                alt=""
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="full-width" v-else>
                      <textarea
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                        autofocus
                        class="area-input-outline wider"
                        placeholder="Provide additional instructions"
                        v-autoresize
                        v-model="articleInstructions"
                      />

                      <div class="row">
                        <button @click="toggleArticleRegenerate" class="secondary-button">
                          Cancel
                        </button>

                        <button
                          @click="
                            regenerateArticleSummary(
                              article.link,
                              article.summary,
                              articleInstructions,
                            )
                          "
                          :disabled="
                            articleSummaryLoading || loading || summaryLoading || savingSearch
                          "
                          class="primary-button"
                        >
                          <img
                            v-if="articleSummaryLoading && loadingUrl === article.link"
                            class="rotate"
                            height="14px"
                            src="@/assets/images/loading.svg"
                            alt=""
                          />
                          {{
                            articleSummaryLoading && loadingUrl === article.link
                              ? 'Submitting'
                              : 'Submit'
                          }}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import ChatTextBox from '../Chat/ChatTextBox.vue'
import Reports from '../pr/Reports.vue'
import { Comms } from '@/services/comms'
import User from '@/services/users'
import { mapActions } from 'vuex'

export default {
  name: 'SummariesSinglePage',
  components: {
    ChatTextBox,
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
    Reports,
  },
  props: {
    selectedSearch: {
      type: Object,
    },
    page: {
      type: String,
    },
  },
  data() {
    return {
      addedClip: false,
      showSummaryInput: true,
      contentType: 'Instructions',
      showSummaryInstructions: true,
      showingViews: false,
      summarizing: false,
      detailModalOpen: false,
      detialText: null,
      detailTitle: null,
      currentAlertId: null,
      alertSet: false,
      emailText: 'Enable',
      showNotifyBanner: false,
      currentAlert: null,
      emailAlerts: [],
      alertTIme: '',
      notifiedList: [],
      savingAlert: false,
      notifyModalOpen: false,
      formattedDate: '',
      dateStart: null,
      dateEnd: null,
      contentModalOpen: false,
      contentInstructions: null,
      contentUrl: null,
      showExpireModal: false,
      checkInterval: null,
      currentRow: null,
      addedArticles: [],
      clipLoading: false,
      uploadLink: null,
      success: true,
      articleBannerText: '',
      showArticleBanner: false,
      showArticleGenerateDropdown: false,
      optionIndex: null,
      contentLoading: false,
      addedClips: [],
      ShowReport: false,
      sentSummaryEmail: false,
      sendingSummaryEmail: false,
      sendSummaryEmailText: 'Email',
      showingPromptDropdown: false,
      sourceSummary: null,
      buttonText: 'Article Summary',
      AllUserTweets: {},
      mainView: 'news',
      savedSearch: null,
      tweets: [],
      tweetMedia: null,
      tweetUsers: null,
      articleInstructions: null,
      showUpdateBanner: false,
      showArticleRegenerate: false,
      showSaveName: false,
      isTyping: false,
      searchName: null,
      searchId: null,
      textIndex: 0,
      typedMessage: '',
      tweetError: '',
      savingSearch: false,
      starterNum: 0,
      newSearch: '',
      newTemplate: '',
      additionalSources: '',
      outputInstructions: '',
      loading: false,
      summaryLoading: false,
      shouldCancel: false,
      regenModal: false,
      filteredArticles: [],
      summary: '',
      booleanString: null,
      metaData: { clips: [] },
      newSummary: false,
      addingPrompt: false,
      addingSources: false,
      loadingUrl: null,
      articleSummaryLoading: false,
      paidModal: false,
      showingDropdown: false,
      showGenerateDropdown: false,
      selectedOption: null,
      successModal: false,
      errorModal: false,
      selectedDateTime: '',
      articleGenerateOptions: [
        { name: 'Press Release', value: `Press Release` },
        { name: 'Statement', value: 'Statement' },
        { name: `Media Pitch`, value: `Media Pitch` },
        { name: `Blog Post`, value: `Blog Post` },
        { name: `LinkedIn Post`, value: `LinkedIn Post` },
        { name: `Twitter Post`, value: `Twitter Post` },
        { name: 'Email', value: 'Email' },
        { name: 'Other', value: '' },
      ],
      generateOptions: [
        { name: 'Basic summary', value: 'Summarize the news' },
        {
          name: 'Advanced summary',
          value: `Summarize the news for XXX, provide sentiment, creative ways they can newsjack this coverage, and list 5 journalists from Tier 1 publications that will write about this, along with creative pitching tips`,
        },
        {
          name: 'PR agency',
          value:
            'As XXX PR agency, provide an update on what the competition is doing along with super creative ways to newsjack this coverage',
        },
        {
          name: `List top headlines`,
          value: `List 5 of the most important headlines ( include source name + journalist) and the impact on XXX`,
        },
        {
          name: `List 10 journalists`,
          value: `List 10 journalists from Tier 1 publications and creative tips to pitch them`,
        },
        {
          name: `Media report`,
          value: `Create a media monitoring report for XXX. Include top sources (based on popularity and size), number of articles, sentiment, and any other important metrics`,
        },
        {
          name: 'Address negative coverage',
          value: 'Respond to all the negative coverage on behalf of XXX',
        },
        {
          name: 'Q & A',
          value: 'Generate 5 questions & answers journalists would ask based on this news',
        },
        {
          name: 'Write media pitch',
          value: 'Create a media pitch on behalf of XXX based on this coverage',
        },
        {
          name: 'Write blog post',
          value: 'Write a highly engaging blog post based on this coverage for XXX',
        },
        {
          name: 'Issue statement',
          value: 'Issue a statement on behalf of XXX based on this covarage',
        },
      ],
      upgradeMessage: 'You have reached your usage limit for the month. Please upgrade your plan.',
      copyTip: 'Copy',
      searchSuggestions: [
        // 'XXX',
        `XXX competitors (list them out) not XXX`,
        `XXX and viral and TikTok`,
        `List out topics XXX would care about`,
        'XXX no stock related news',
        'XXX no exclusions',
        'University of XXX no sports related news',
        'XXX Hospital no ER related stories',
      ],
      promptSuggestions: [
        `Summarize the news for XXX`,
        `Summarize the news for XXX, provide sentiment analysis, and the PR impact of this coverage`,
        `Trends about XXX`,
        `List 5 of the most important headlines ( include source name + journalist) about XXX`,
        `Find up to 10 journalists (from top pubs, include pitching tips) writing about XXX`,
        `Create a media monitoring report for XXX. List top sources and journalist (based on popularity and size of publication), sentiment analysis, and any other important metrics`,
        // `Respond to all the negative coverage about XXX on behalf of XXX`,
        `Generate 5 questions & answers journalists would ask about XXX`,
        `Write an informative media pitch on behalf of XXX about XXX`,
        `Write an engaging blog post on behalf of XXX about XXX`,
        `Issue a blunt statement on behalf of XXX about XXX`,
      ],
    }
  },
  created() {
    // this.checkInterval = setInterval(this.checkTokenExpiry, 60000)
    this.addedClips = this.$store.state.currentReportClips
    this.shouldCancel = false

    console.log('this.$route', this.$route.query.success)

    if (this.$route.query && this.$route.query.success) {
      if (this.$route.query.success === 'true') {
        this.successModal = true
      } else {
        this.errorModal = true
      }
    }

    const today = new Date()
    const sevenDaysAgo = new Date(today)
    sevenDaysAgo.setDate(today.getDate() - 7)

    // Format the dates as YYYY-MM-DD strings (required for <input type="date">)
    this.dateStart = sevenDaysAgo.toISOString().split('T')[0]
    this.dateEnd = today.toISOString().split('T')[0]

    const defaultTime = new Date()
    defaultTime.setHours(8, 0)
    this.selectedTime = defaultTime.toISOString().slice(0, 16)
  },
  watch: {
    typedMessage: 'changeIndex',
    currentSearch(newVal, oldVal) {
      if (newVal && newVal.id !== (oldVal ? oldVal.id : null)) {
        this.setSearch(newVal)
      }
    },
  },
  mounted() {
    this.getEmailAlerts()
    window.addEventListener('scroll', this.checkScroll)
    // window.addEventListener('beforeunload', () => {
    //   // Abort the Axios request when the user leaves the page
    //   this.controller.abort();
    // });
    // this.updateMessage()
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.checkScroll)
    // window.removeEventListener('beforeunload', () => {
    //   this.controller.abort();
    // });
    this.abortFunctions()
  },
  methods: {
    toggleDetailModal() {
      this.detailModalOpen = !this.detailModalOpen
    },
    changeEmailText() {
      if (!this.isPaid) {
        this.emailText = 'Upgrade to Pro!'
      } else {
        return
      }
    },
    defaultEmailText() {
      if (!this.isPaid) {
        this.emailText = 'Enable'
      } else {
        return
      }
    },
    setCurrentAlert(id = null) {
      if (id) {
        this.currentAlert = this.emailAlerts.filter((alert) => alert.search === id)[0]
      } else {
        this.currentAlert = this.emailAlerts.filter((alert) => alert.search === this.searchId)[0]
      }
      this.getEmailAlerts()
    },
    async testEmailAlert() {
      try {
        Comms.api.testEmailAlert({ alert_id: this.currentAlertId }).then((response) => {
          this.toggleShowNotifyBanner()
          this.toggleNotifyModal()
        })
      } catch (e) {
        console.log(e)
      }
    },
    async removeEmailAlert() {
      console.log(this.currentAlert)
      try {
        Comms.api.removeEmailAlert({ id: this.currentAlert.id }).then((response) => {
          this.getEmailAlerts()
          this.toggleShowNotifyBanner()
        })
      } catch (e) {
        console.log(e)
      }
    },
    async getEmailAlerts() {
      try {
        Comms.api.getEmailAlerts().then((response) => {
          this.emailAlerts = response.results
          this.notifiedList = response.results.map((alert) => alert.search)
        })
      } catch (e) {
        console.log(e)
      }
    },
    async addEmailAlert() {
      this.savingAlert = true
      try {
        Comms.api
          .addEmailAlert({
            search: this.searchId,
            run_at: this.formattedDate,
            user: this.user.id,
            title: this.searchName,
          })
          .then((response) => {
            this.currentAlertId = response.id
            this.getEmailAlerts()
            this.toggleShowNotifyBanner()
            setTimeout(() => {
              this.setCurrentAlert(id)
            }, 1000)
          })
      } catch (e) {
        console.log(e)
      } finally {
        setTimeout(() => {
          this.savingAlert = false
          this.alertSet = true
        }, 1000)
      }
    },
    toggleShowNotifyBanner() {
      setTimeout(() => {
        this.showNotifyBanner = true
      }, 1000)
      setTimeout(() => {
        this.showNotifyBanner = false
      }, 3000)
    },
    calculateDate(selectedTime) {
      const [hours, minutes] = selectedTime.split(':').map(Number)

      if (
        isNaN(hours) ||
        isNaN(minutes) ||
        hours < 0 ||
        hours > 23 ||
        minutes < 0 ||
        minutes > 59
      ) {
        this.formattedDate = 'Invalid time input'
        return
      }

      const currentDate = new Date()
      currentDate.setHours(hours, minutes, 0, 0)

      const year = currentDate.getFullYear()
      const month = String(currentDate.getMonth() + 1).padStart(2, '0')
      const day = String(currentDate.getDate()).padStart(2, '0')
      const formattedTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(
        2,
        '0',
      )}:00.000000`

      this.formattedDate = `${year}-${month}-${day}T${formattedTime}`
    },
    toggleNotifyModal() {
      if ((this.searchSaved || this.savedSearch) && this.isPaid) {
        this.alertSet = false
        this.notifyModalOpen = !this.notifyModalOpen
      }
    },
    closeContentModal() {
      if (!this.contentLoading) {
        this.contentModalOpen = false
      } else {
        return
      }
    },
    setRow(i) {
      this.currentRow = i
    },
    setAddedClips(clips) {
      this.addedClips = clips
    },
    removeRow() {
      this.currentRow = null
    },
    toggleArticleGenerateDropdown() {
      this.showArticleGenerateDropdown = !this.showArticleGenerateDropdown
    },
    toggleGenerateDropdown() {
      this.showGenerateDropdown = !this.showGenerateDropdown
    },
    selectOption(val, index) {
      if (!this.contentLoading) {
        this.optionIndex = index
        this.contentLoading = true
        this.selectedOption = val
        this.setPitchContent()
      }
    },
    setContentInstructions(name, val) {
      this.showGenerateDropdown = false
      // this.contentType = name
      this.newTemplate = val
    },
    selectArticleOption(url, val, index) {
      if (!this.contentLoading) {
        this.contentInstructions = ''
        this.showGenerateDropdown = false
        this.showArticleGenerateDropdown = false
        this.contentModalOpen = true
        this.optionIndex = index
        this.contentUrl = url
        this.contentType = val
        this.contentInstructions = `Create a ${val} for XXX, newsjacking this article`
        // this.setArticlePitchContent(url,sum)
      }
    },
    closeSuccessModal() {
      this.$router.push({ name: 'PRSummaries' })
      this.$router.go()
      this.successModal = false
    },
    setPitchContent() {
      let content = {
        summary: this.summary,
        term: this.newSearch,
        type: this.selectedOption,
      }
      this.$store.commit('setGeneratedContent', content)
      setTimeout(() => {
        this.$router.push({ name: 'Pitches' })
      }, 500)
    },
    unbindClickOutsidePromptMenu() {
      const el = document.getElementById('instructions')

      if (el && el._clickOutsideHandler) {
        // Remove the event listener
        document.body.removeEventListener('click', el._clickOutsideHandler)
      }
    },
    bindClickOutsidePromptMenu() {
      // Get the directive element where you want to bind the listener
      const el = document.getElementById('instructions')

      if (el) {
        // Define the clickOutsideHandler function (the same logic as in your directive)
        function clickOutsideHandler(e) {
          if (!el.contains(e.target)) {
            // Trigger your functionality when clicked outside the element
            this.hidePromptDropdown() // Replace with your actual functionality
          }
        }

        // Attach the clickOutsideHandler to the element
        el._clickOutsideHandler = clickOutsideHandler.bind(this)

        // Add the event listener to the document body
        document.body.addEventListener('click', el._clickOutsideHandler)
      }
    },
    setArticlePitchContent(sum) {
      let content = {
        summary: sum,
        term: this.newSearch,
        type: this.selectedOption,
      }
      this.$store.commit('setGeneratedContent', content)
      setTimeout(() => {
        this.$router.push({ name: 'Pitches' })
      }, 500)
    },
    clearClips() {
      this.addedClips = []
      this.metaData = { clips: [] }
      // this.savedSearch.meta_data = {...this.savedSearch.meta_data, clips: []}
      this.$store.dispatch('updateCurrentReportClips', this.addedClips)
      // this.updateMetaData()
    },
    removeArticle(title) {
      const newArticles = this.addedArticles.filter((article) => article.title !== title)
      this.addedArticles = newArticles
    },
    removeClip(title) {
      const cats = this.$store.state.categories
      if (Object.keys(cats).length) {
        const newCats = { ...cats }
        for (let key in cats) {
          const clips = cats[key]
          const filteredClips = clips.filter((clip) => clip.title !== title && clip.text !== title)
          newCats[key] = filteredClips
        }
        this.$store.dispatch('updateCategories', newCats)
      }
      const newClips = this.addedClips.filter((clip) => clip.title !== title && clip.text !== title)
      this.addedClips = newClips
      this.$store.dispatch('updateCurrentReportClips', this.addedClips)
      if (this.currentSearch) {
        this.metaData = { ...this.currentSearch.meta_data, clips: newClips }
        // this.updateMetaData()
      }
    },
    toggleReport() {
      if (!this.isPaid) {
        this.openPaidModal('Upgrade your plan in order to create reports.')
      } else {
        this.ShowReport = !this.ShowReport
      }
    },
    async uploadArticle() {
      this.summary = null
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      this.clipLoading = true
      // this.showSummaryInstructions = false
      try {
        await Comms.api
          .uploadLink({
            url: this.uploadLink,
          })
          .then((response) => {
            this.success = true
            this.addClipFromUrl(response)
            this.articleBanner('Article added!')
          })
      } catch (e) {
        this.addedArticles = []
        this.success = false
        console.log(e)
        this.articleBanner('Error adding article!')
      } finally {
        this.clipLoading = false
        this.uploadLink = null
      }
    },
    articleBanner(text) {
      this.articleBannerText = text
      this.showArticleBanner = true
      setTimeout(() => {
        this.showArticleBanner = false
      }, 2000)
    },
    addClipFromUrl(clip) {
      clip.author = clip.author[0]
      clip['search'] = this.newSearch
      this.addedArticles = [clip]
      this.getSourceSummary()
    },
    addClip(clip) {
      if (Array.isArray(clip.author)) {
        clip.author = clip.author[0]
      }
      clip['search'] = this.newSearch
      if (this.addedClips && this.addedClips.length < 20) {
        this.addedClip = true
        setTimeout(() => {
          this.addedClip = false
        }, 500)
        if (!clip.image_url && (clip.attachments || clip.edit_history_tweet_ids)) {
          let tweetImg = ''
          if (clip.attachments) {
            for (let i = 0; i < this.tweetMedia.length; i++) {
              const media = this.tweetMedia[i]
              if (media.media_key === clip.attachments.media_keys[0]) {
                if (media.type === 'photo') {
                  tweetImg = media.url
                  break
                } else if (media.type === 'video') {
                  // tweetImg = media.variants[1].url
                  // break;
                } else if (media.type === 'animated_gif') {
                  // tweetImg = media.variants[0].url
                  // break;
                }
              }
            }
          }
          if (!tweetImg) {
            tweetImg = clip.user.profile_image_url
          }
          clip.image_url = tweetImg
        }
        if (clip.attachments) {
          const mediaURLs = []
          for (let i = 0; i < clip.attachments.media_keys.length; i++) {
            const mediaKey = clip.attachments.media_keys[i]
            const media = this.tweetMedia.filter((tm) => tm.media_key === mediaKey)
            if (media[0]) {
              if (media[0].url) {
                mediaURLs.push({ url: media[0].url, type: 'image' })
              } else if (media[0].variants) {
                if (media[0].type === 'video') {
                  mediaURLs.push({ url: media[0].variants[1].url, type: 'video' })
                } else if (media[0].type === 'animated_gif') {
                  mediaURLs.push({ url: media[0].variants[0].url, type: 'animated_gif' })
                }
              }
            }
          }
          clip.attachments.mediaURLs = mediaURLs
        }
        const categories = this.$store.state.categories
        const categoryNames = Object.keys(categories)
        if (categoryNames.length) {
          clip.category = categoryNames[categoryNames.length - 1]
          categories[categoryNames[categoryNames.length - 1]].push(clip)
          this.$store.dispatch('updateCategories', categories)
        } else {
          clip.category = null
          this.addedClips.push(clip)
          this.$store.dispatch('updateCurrentReportClips', this.addedClips)
        }
        if (this.currentSearch) {
          this.metaData = { ...this.currentSearch.meta_data, clips: this.addedClips }
          // this.updateMetaData()
        }
      } else {
        return
      }
    },
    editClip(title, summary) {
      let clip = this.addedClips.filter((clip) => clip.title === title)[0]
      clip['summary'] = summary
      const newClips = this.addedClips.filter((clip) => clip.title !== title)
      newClips.unshift(clip)
      this.addedClips = newClips
      this.$store.dispatch('updateCurrentReportClips', this.addedClips)
      if (this.currentSearch) {
        this.metaData = { ...this.currentSearch.meta_data, clips: newClips }
        // this.updateMetaData()
      }
    },
    soonButtonText() {
      this.buttonText = 'Coming Soon!'
    },
    defaultButtonText() {
      this.buttonText = 'Article Summary'
    },
    openTweet(username, id) {
      window.open(`https://twitter.com/${username}/status/${id}`, '_blank')
    },
    addSuggestion(ex) {
      this.newSearch = ex
      this.hideDropdown()
    },
    addPromptSuggestion(ex) {
      this.newTemplate = ex
      this.hidePromptDropdown()
    },
    async copyArticleSummary(article) {
      try {
        const cleanedSummary = article
          .split('<strong>')
          .filter((item) => item !== '<strong>')
          .join('')
          .split('</strong>')
          .filter((item) => item !== '</strong>')
          .join('')
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    async copyText() {
      try {
        const cleanedSummary = this.summary
          .split('<strong>')
          .filter((item) => item !== '<strong>')
          .join('')
          .split('</strong>')
          .filter((item) => item !== '</strong>')
          .join('')
        await navigator.clipboard.writeText(cleanedSummary)
        this.copyTip = 'Copied!'

        setTimeout(() => {
          this.copyTip = 'Copy'
        }, 2000)
      } catch (err) {
        console.error('Failed to copy text: ', err)
      }
    },
    showDropdown() {
      this.showingDropdown = true
    },
    hideDropdown() {
      this.showingDropdown = false
    },
    showPromptDropdown() {
      this.showingPromptDropdown = true
    },
    hidePromptDropdown() {
      this.showingPromptDropdown = false
    },
    resetAll() {
      this.clearNewSearch()
      this.newSearch = ''
      this.addedClips = []
      this.filteredArticles = []
      this.metaData = { clips: [] }
      this.$emit('change-search', null)
      this.$store.dispatch('setSearch', null)
      this.summary = ''
    },
    resetSearch() {
      this.clearNewSearch()
      this.addedClips = []
      // this.$store.dispatch('updateCurrentReportClips', this.addedClips)
      this.metaData = { clips: [] }
      this.$emit('change-search', null)
      this.$store.dispatch('setSearch', null)
      this.summary = ''
    },
    bindClickOutsideSearchMenu() {
      const el = document.getElementById('prompt-search')

      if (el) {
        function clickOutsideSearchMenuHandler(e) {
          if (!el.contains(e.target)) {
            // Trigger the functionality to close the search menu dropdown
            this.hideDropdown() // Replace with your actual functionality
          }
        }

        el._clickOutsideSearchMenuHandler = clickOutsideSearchMenuHandler.bind(this)

        document.body.addEventListener('click', el._clickOutsideSearchMenuHandler)
      }
    },
    switchMainView(view) {
      this.resetAll()
      // if (view === 'news') {
      //   this.deselectOpp()
      // } else if (view !== 'meetings') {
      //   this.deselectMeeting()
      // }
      if (view !== this.mainView) {
        if (this.mainView === 'website') {
          this.unbindClickOutsidePromptMenu()
          this.mainView = view
        } else {
          this.mainView = view
        }
        if (this.mainView !== 'website') {
          setTimeout(() => {
            this.bindClickOutsideSearchMenu()
          }, 200)
        }
      }
    },
    formatNumber(num) {
      if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1).replace(/\.0$/, '') + 'B'
      }
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
      }
      return num.toString()
    },
    toggleArticleRegenerate() {
      this.showArticleRegenerate = !this.showArticleRegenerate
    },
    toggleSaveName() {
      this.showSaveName = !this.showSaveName
    },
    setSearch(search) {
      this.showSummaryInstructions = true
      this.summarizing = false
      this.savedSearch = search
      this.summary = ''
      this.searchId = search.id
      this.searchName = search.name
      this.newSearch = search.input_text
      this.booleanString = search.search_boolean
      this.newTemplate = search.instructions
      this.metaData = search.meta_data
      this.addedClips = this.$store.state.currentReportClips
      // this.addedClips = search.meta_data.clips ? search.meta_data.clips : []
      this.mainView = search.type === 'SOCIAL_MEDIA' ? 'social' : 'news'
      this.generateNewSearch(true, search.search_boolean)
      this.setCurrentAlert()
    },
    changeIndex() {
      setTimeout(() => {
        this.isTyping = false
        this.typedMessage = ''
      }, 5750)
      setTimeout(() => {
        this.updateMessage()
      }, 5850)
    },
    updateMessage() {
      this.textIndex = Math.floor(Math.random() * this.searchMessages.length)
      this.isTyping = true
      this.typedMessage = this.searchMessages[this.textIndex]
    },
    scrollToTop() {
      setTimeout(() => {
        this.$refs.loadedContent.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    },
    scrollToTopDivider() {
      setTimeout(() => {
        this.$refs.topDivider.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    },
    removeSource() {
      this.additionalSources = ''
      this.addingSources = !this.addingSources
    },
    removePrompt() {
      this.newTemplate = ''
      this.addingPrompt = !this.addingPrompt
    },
    toggleAddPrompt() {
      this.addingPrompt = !this.addingPrompt
    },
    toggleAddSource() {
      this.addingSources = !this.addingSources
    },
    getTimeDifferenceInMinutes(dateString) {
      if (dateString) {
        const currentDate = new Date()
        const givenDate = new Date(dateString)

        if (
          givenDate.getDate() === currentDate.getDate() &&
          givenDate.getMonth() === currentDate.getMonth() &&
          givenDate.getFullYear() === currentDate.getFullYear()
        ) {
          const timeDifferenceInMilliseconds = currentDate - givenDate
          const timeDifferenceInMinutes = Math.floor(timeDifferenceInMilliseconds / (1000 * 60))
          if (timeDifferenceInMinutes >= 60) {
            const timeDifferenceInHours = Math.floor(timeDifferenceInMinutes / 60)
            const remainingMinutes = timeDifferenceInMinutes % 60
            return `${timeDifferenceInHours}h`
          } else {
            return `${timeDifferenceInMinutes}m`
          }
        } else {
          let month
          let day
          let year
          if (Number(givenDate.getMonth() + 1)) {
            month = givenDate.getMonth() + 1
          } else {
            month = '--'
          }
          if (Number(givenDate.getDate())) {
            day = givenDate.getDate()
          } else {
            day = '--'
          }
          if (Number(givenDate.getFullYear())) {
            year = givenDate.getFullYear()
          } else {
            year = '--'
          }
          return `${month}/${day}/${year}`
        }
      } else {
        return '--/--/----'
      }
    },
    openPaidModal(msg) {
      this.upgradeMessage = msg
      this.paidModal = true
    },
    closePaidModal() {
      this.paidModal = false
    },
    goToContact() {
      window.open('https://managr.ai/contact', '_blank')
    },
    stopLoading() {
      this.loading = false
      this.summaryLoading = false
    },
    async generateNewSearch(saved = false, boolean = '') {
      this.changeSearch({ search: null, template: null })
      this.savedSearch = null
      this.showGenerateDropdown = false
      if (!this.isPaid && this.searchesUsed >= 10) {
        this.openPaidModal(
          'You have reached your usage limit for the month. Please upgrade your plan.',
        )
        return
      }
      this.sendSummaryEmailText = 'Email'
      this.sentSummaryEmail = false
      this.addedClips = this.$store.state.currentReportClips
      if (this.shouldCancel) {
        return this.stopLoading()
      }
      if (this.mainView !== 'website' && (!this.newSearch || this.newSearch.length < 3)) {
        return
      } else if (this.mainView === 'social') {
        this.closeRegenModal()
        this.getTweets()
      } else if (this.mainView === 'website') {
        this.closeRegenModal()
        this.getSourceSummary()
      } else {
        this.closeRegenModal()
        this.loading = true
        this.changeSearch({ search: this.booleanString, template: this.newTemplate })
        try {
          if (this.shouldCancel) {
            return this.stopLoading()
          }
          await this.getClips(saved, boolean).then(() => {
            if (this.filteredArticles.length) {
              if (saved) {
                this.getSummary(this.filteredArticles, this.newTemplate)
              } else {
                this.getSummary(this.filteredArticles, this.newSearch)
              }
            }
          })
          if (this.shouldCancel) {
            return this.stopLoading()
          }
          if (saved) {
            this.updateSearch()
          }
          this.refreshUser()
        } catch (e) {
          console.log(e)
        }
      }
    },
    async getSourceSummary() {
      // this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      this.summaryLoading = true
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        let response
        if (this.addedArticles.length === 1) {
          response = await this.getArticleSummary(this.addedArticles[0].link, this.newTemplate)
          this.summary = response
        } else {
          response = await this.getSummary(this.addedArticles, this.newTemplate)
        }
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        if (this.searchSaved) {
          this.updateSearch()
        }
        this.refreshUser()
        this.summaryLoading = false
      } catch (e) {
        console.log(e)
      } finally {
        this.summarizing = true
      }
    },
    async updateMetaData() {
      try {
        await Comms.api
          .upateSearch({
            id: this.searchId,
            meta_data: this.metaData,
          })
          .then((response) => {
            this.savedSearch = {
              name: this.searchName,
              input_text: this.newSearch,
              meta_data: this.metaData,
              search_boolean: this.booleanString,
              instructions: this.newTemplate,
            }
            // this.$store.dispatch('setSearch', this.savedSearch)
          })
      } catch (e) {
        console.log('ERROR UPDATING SEARCH', e)
      }
    },
    async updateSearch() {
      console.log('I AM MAKING IT HERE', this.newTemplate)
      try {
        await Comms.api
          .upateSearch({
            id: this.searchId,
            name: this.searchName,
            input_text: this.newSearch,
            meta_data: this.metaData,
            search_boolean: this.booleanString,
            instructions: this.newTemplate,
          })
          .then((response) => {
            this.savedSearch = {
              name: this.searchName,
              input_text: this.newSearch,
              meta_data: this.metaData,
              search_boolean: this.booleanString,
              instructions: this.newTemplate,
            }
            // this.$store.dispatch('setSearch', this.savedSearch)
          })
      } catch (e) {
        console.log('ERROR UPDATING SEARCH', e)
      }
    },
    clearNewSearch() {
      this.summary = null
      this.summarizing = false
      // this.newSearch = ''
      this.newTemplate = ''
      this.searchName = ''
      this.metaData = { clips: [] }
      this.addedArticles = []
    },
    openRegenModal() {
      this.regenModal = true
    },
    closeRegenModal() {
      this.regenModal = false
    },
    changeSearch(search) {
      this.$emit('change-search', search)
    },
    async createSearch() {
      this.showSaveName = false
      this.savingSearch = true
      try {
        const response = await Comms.api
          .createSearch({
            name: this.searchName,
            input_text: this.newSearch,
            search_boolean: this.booleanString,
            instructions: this.newTemplate ? this.newTemplate : this.newSearch,
            meta_data: this.metaData,
            type: this.mainView === 'news' ? 'NEWS' : 'SOCIAL_MEDIA',
          })
          .then((response) => {
            if (response.id) {
              this.searchId = response.id
              this.showUpdateBanner = true
              this.savedSearch = {
                name: response.name,
                input_text: this.newSearch,
                meta_data: this.metaData,
                search_boolean: this.booleanString,
                instructions: this.newTemplate ? this.newTemplate : this.newSearch,
              }
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.savingSearch = false
        this.$store.dispatch('getSearches')
        setTimeout(() => {
          this.showUpdateBanner = false
        }, 2000)
      }
    },
    async sendSummaryEmail() {
      this.sendingSummaryEmail = true
      try {
        this.sentSummaryEmail = true
        console.log('this.filteredArticles', this.filteredArticles)
        let clips
        if (this.mainView === 'social') {
          clips = this.tweets.filter((clip, i) => {
            if (i < 10) {
              return clip
            }
          })
        } else if (this.mainView === 'news') {
          clips = this.filteredArticles.filter((clip, i) => {
            if (i < 10) {
              return clip
            }
          })
        } else {
          clips = this.addedArticles
        }
        await Comms.api.sendSummaryEmail({ summary: this.summary, clips })
        this.sendSummaryEmailText = 'Sent!'
        this.$toast('Email sent!', {
          timeout: 2000,
          position: 'top-left',
          type: 'success',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } catch (e) {
        console.log('Error in sendSummaryEmail:', e)
        this.sentSummaryEmail = false
        this.$toast('Something went wrong, please try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.sendingSummaryEmail = false
      }
    },
    abortFunctions() {
      this.shouldCancel = true

      for (let key in this.controllers) {
        this.controllers[key].controller.abort()
      }
      // update controllers here
      this.$store.dispatch('updateAbortController', {})
    },
    async getClips(saved = false, boolean = '') {
      this.summary = null
      this.showingDropdown = false
      try {
        // update controllers here
        this.$store.dispatch('updateAbortController', {
          ...this.$store.state.abortControllers,
          getClips: { name: 'getClips', controller: new AbortController() },
        })
        await Comms.api
          .getClips(
            {
              search: this.newSearch,
              boolean: boolean,
              user_id: this.user.id,
              date_from: this.dateStart,
              date_to: this.dateEnd,
            },
            this.controllers.getClips.controller.signal,
          )
          .then((response) => {
            this.filteredArticles = response.articles
            this.booleanString = response.string
            if (!saved) {
              this.clearNewSearch()
            }
          })
      } catch (e) {
        this.clearNewSearch()
        this.filteredArticles = []
        console.log(e)
      } finally {
        const newAbortControllers = { ...this.$store.state.abortControllers }
        delete newAbortControllers.getClips
        this.$store.dispatch('updateAbortController', newAbortControllers)
        this.loading = false
      }
    },
    async getTweets(boolean = null) {
      this.summary = null
      this.loading = true
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        await Comms.api
          .getTweets({
            search: this.newSearch,
            user_id: this.user.id,
          })
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            if (response.tweets) {
              this.tweets = response.tweets
              this.tweetMedia = response.includes.media
              this.booleanString = response.string
              // this.getTweetSummary()
            }
            this.clearNewSearch()
            this.showingDropdown = false
          })
      } catch (e) {
        this.tweetError = e.data.error
        this.booleanString = e.data.string
        this.summaryLoading = false
        this.tweets = []
        this.tweetMedia = null
        this.clearNewSearch()
      } finally {
        this.loading = false
      }
    },
    prepareTweetSummary(tweets) {
      let tweetList = []
      for (let i = 0; i < tweets.length; i++) {
        tweetList.push(
          'Name :' +
            tweets[i].user.name +
            ' Tweet: ' +
            tweets[i].text +
            ' Follower count: ' +
            tweets[i].user.public_metrics.followers_count +
            ' Date: ' +
            tweets[i].created_at,
        )
      }
      return tweetList
    },
    getArticleDescriptions(articles) {
      return articles.map(
        (a) =>
          `Content:${a.description} Date:${a.publish_date}, Source:${a.source.name}, Author:${a.author}`,
      )
    },
    async getTweetSummary(instructions = '') {
      let tweets = this.prepareTweetSummary(this.tweets)
      this.summaryLoading = true
      this.summary = ''
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        await Comms.api
          .getTweetSummary({
            tweets: tweets,
            search: this.newSearch,
            instructions: this.newTemplate,
          })
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            this.summary = response.summary
            this.refreshUser()
          })
      } catch (e) {
        console.log('Error in getTweetSummary', e)
        this.$toast('Something went wrong, please try again.', {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.summarizing = true
        this.summaryLoading = false
        this.scrollToTop()
      }
    },
    async getSummary(clips, instructions = '') {
      console.log(instructions)
      const allClips = this.getArticleDescriptions(clips)
      this.summaryLoading = true
      let openAiDown = false
      this.summary = ''
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        this.$store.dispatch('updateAbortController', {
          ...this.$store.state.abortControllers,
          getSummary: { name: 'getSummary', controller: new AbortController() },
        })
        await Comms.api
          .getSummary(
            {
              clips: allClips,
              search: this.newSearch,
              instructions: instructions,
            },
            this.controllers.getSummary.controller.signal,
          )
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            if (this.searchSaved) {
              this.updateSearch()
            }
            this.summary = response.summary
          })
      } catch (e) {
        console.log('Error in getSummary', e)
        if (
          e.data &&
          e.data.summary === "Unknown exception: 'NoneType' object is not subscriptable"
        ) {
          this.$toast('OpenAI is down, please try again later.', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
          openAiDown = true
        } else {
          this.$toast('Something went wrong, please try again.', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      } finally {
        if (openAiDown) {
          // this.changeSearch({ search: null, template: null })
          this.resetSearch()
          this.abortFunctions()
          return this.stopLoading()
        }
        const newAbortControllers = { ...this.$store.state.abortControllers }
        delete newAbortControllers.getClips
        this.$store.dispatch('updateAbortController', newAbortControllers)
        this.summarizing = true
        this.summaryLoading = false
        this.scrollToTop()
      }
    },
    async regenerateArticleSummary(url, summary, instructions) {
      let selectedClip = this.addedArticles.length
        ? this.addedArticles.filter((art) => art.link === url)[0]
        : this.filteredArticles.filter((art) => art.link === url)[0]

      this.articleSummaryLoading = true
      this.loadingUrl = url

      try {
        const response = await Comms.api.regenerateArticleSummary({
          url,
          summary: summary,
          instructions: instructions,
        })
        selectedClip['summary'] = response.summary
        if (!this.addedArticles.length) {
          this.filteredArticles = this.filteredArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.filteredArticles.unshift(selectedClip)
        } else {
          this.addedArticles = this.addedArticles = this.addedArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.addedArticles.unshift(selectedClip)
        }

        this.refreshUser()
        this.scrollToTopDivider()
      } catch (e) {
        console.log(e)
      } finally {
        this.showArticleRegenerate = false
        this.articleSummaryLoading = false
        this.loadingUrl = null
      }
    },
    async getArticleSummary(url, instructions = null, length = 1000) {
      let selectedClip = this.addedArticles.length
        ? this.addedArticles.filter((art) => art.link === url)[0]
        : this.filteredArticles.filter((art) => art.link === url)[0]

      this.articleSummaryLoading = true
      this.loadingUrl = url

      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        const response = await Comms.api.getArticleSummary({
          url: url,
          search: this.newSearch,
          instructions: instructions,
          length: length,
        })
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        selectedClip['summary'] = response.summary
        if (!this.addedArticles.length) {
          this.filteredArticles = this.filteredArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.filteredArticles.unshift(selectedClip)
        } else {
          this.addedArticles = this.addedArticles = this.addedArticles.filter(
            (clip) => clip.title !== selectedClip.title,
          )
          this.addedArticles.unshift(selectedClip)
        }

        if (this.shouldCancel) {
          return this.stopLoading()
        }
        this.refreshUser()
        this.scrollToTopDivider()
        return response.summary
      } catch (e) {
        console.log(e)
        // this.$toast('Could not access article URL', {
        //   timeout: 2000,
        //   position: 'top-left',
        //   type: 'error',
        //   toastClassName: 'custom',
        //   bodyClassName: ['custom'],
        // })
      } finally {
        this.showArticleRegenerate = false
        this.articleSummaryLoading = false
        this.loadingUrl = null
      }
    },
    async generateContent() {
      this.contentLoading = true
      let selectedClip = this.addedArticles.length
        ? this.addedArticles.filter((art) => art.link === this.contentUrl)[0]
        : this.filteredArticles.filter((art) => art.link === this.contentUrl)[0]

      try {
        await Comms.api
          .generateContent({
            url: this.contentUrl,
            instructions: this.contentInstructions,
            style: '',
          })
          .then((response) => {
            if (this.mainView === 'website' && this.addedArticles.length === 1) {
              this.summary = response.content
            } else {
              selectedClip['summary'] = response.content
              if (!this.addedArticles.length) {
                this.filteredArticles = this.filteredArticles.filter(
                  (clip) => clip.title !== selectedClip.title,
                )
                this.filteredArticles.unshift(selectedClip)
              } else {
                this.addedArticles = this.addedArticles = this.addedArticles.filter(
                  (clip) => clip.title !== selectedClip.title,
                )
                this.addedArticles.unshift(selectedClip)
              }
            }

            this.refreshUser()
            this.scrollToTopDivider()
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.contentLoading = false
        this.contentInstructions = null
        this.contentType = null
        this.contentUrl = null
        this.contentModalOpen = false
      }
    },
    changeSummaryChat(type) {
      this.summaryChat = type
      this.scrollToBottom()
    },
    selectArticle(article) {
      this.$store.dispatch('updateSelectedArticle', article)
    },
    saveSelectedArticles() {
      this.getSummary(this.selectedArticles)
      this.selectedArticles = []
      this.changeNew()
    },
    addRemoveSelectedArticles(article) {
      const existingArticle = this.selectedArticles.filter((ar) => ar.link === article.link)[0]
      if (existingArticle) {
        this.selectedArticles = this.selectedArticles.filter((ar) => ar.link !== article.link)
      } else {
        this.selectedArticles.push(article)
      }
    },
    goToArticle(link) {
      window.open(link, '_blank')
    },
    changeRegen() {
      this.regenSummary = !this.regenSummary
    },
    changeNew() {
      this.newSummary = !this.newSummary
    },
    searchTitles() {
      this.filteredArticles = this.articles.filter((article) =>
        article.title.includes(this.filterText),
      )
    },
    refreshUser() {
      User.api
        .getUser(this.user.id)
        .then((user) => {
          this.$store.dispatch('updateUser', user)
          return user
        })
        .catch(() => {
          // do nothing for now
          return null
        })
    },
    scrollToBottom() {
      setTimeout(() => {
        const chatWindow = this.$refs.chatWindow
        setTimeout(() => {
          chatWindow.scrollTop = chatWindow.scrollHeight
        }, 200)
      }, 0)
    },
  },
  computed: {
    clipTitles() {
      if (Object.keys(this.$store.state.categories).length) {
        return this.allCategoryClips
          ? this.allCategoryClips.map((clip) => (clip.title ? clip.title : clip.id))
          : []
      } else {
        return this.addedClips
          ? this.addedClips.map((clip) => (clip.title ? clip.title : clip.id))
          : []
      }
    },
    controllers() {
      return this.$store.state.abortControllers
    },
    allCategoryClips() {
      const cats = this.$store.state.categories
      if (Object.keys(cats).length) {
        let addedClips = []
        for (let key in cats) {
          addedClips = [...addedClips, ...cats[key]]
        }
        return addedClips
      } else return this.addedClips
    },
    messages() {
      return this.$store.state.messages
    },
    userName() {
      return this.$store.state.user.firstName
    },
    user() {
      return this.$store.state.user
    },
    currentSearch() {
      return this.$store.state.currentSearch
    },
    filteredSuggestions() {
      if (!this.newSearch) return this.searchSuggestions
      return this.searchSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.newSearch.toLowerCase()),
      )
    },
    filteredPromptSuggestions() {
      if (!this.newTemplate) return this.promptSuggestions
      return this.promptSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.newTemplate.toLowerCase()),
      )
    },
    isPaid() {
      // const decryptedUser = decryptData(this.$store.state.user, process.env.VUE_APP_SECRET_KEY)
      return !!this.$store.state.user.organizationRef.isPaid
    },
    searchesUsed() {
      let arr = []
      let currentMonth = new Date(Date.now()).getMonth() + 1
      if (currentMonth < 10) {
        currentMonth = `0${currentMonth}`
      } else {
        currentMonth = `${currentMonth}`
      }
      let currentYear = new Date(Date.now()).getFullYear()
      for (let key in this.$store.state.user.metaData) {
        const item = this.$store.state.user.metaData[key]
        const filteredByMonth = item.timestamps.filter((date) => {
          const split = date.split('-')
          return split[1] == currentMonth && split[0] == currentYear
        })
        arr = [...arr, ...filteredByMonth]
      }
      return arr.length
    },
    searchSaved() {
      if (
        this.newSearch &&
        this.currentSearch &&
        this.currentSearch.input_text === this.newSearch
      ) {
        return true
      } else if (this.savedSearch && this.newSearch === this.savedSearch.input_text) {
        return true
      } else {
        return false
      }
    },
    fromNav() {
      return this.$store.state.fromNav
    },
  },
  directives: {
    autoresize: {
      inserted(el) {
        function adjustTextareaHeight() {
          el.style.height = 'auto'
          el.style.height = el.scrollHeight + 'px'
        }

        el.addEventListener('input', adjustTextareaHeight)
        el.addEventListener('focus', adjustTextareaHeight)
        el.addEventListener('textarea-clear', adjustTextareaHeight)
        adjustTextareaHeight()
      },
    },
    clickOutsideMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hideDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
    clickOutsidePromptMenu: {
      bind(el, binding, vnode) {
        // Define a function to handle click events
        function clickOutsideHandler(e) {
          // Check if the clicked element is outside the target element
          if (!el.contains(e.target)) {
            // Trigger the provided method from the binding value
            vnode.context.hidePromptDropdown()
          }
        }

        // Add a click event listener to the document body
        document.body.addEventListener('click', clickOutsideHandler)

        // Store the event listener on the element for cleanup
        el._clickOutsideHandler = clickOutsideHandler
      },
      unbind(el) {
        // Remove the event listener when the directive is unbound
        document.body.removeEventListener('click', el._clickOutsideHandler)
      },
    },
  },
}
</script>
<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

@keyframes typing {
  from {
    width: 0;
  }
  to {
    width: 100%;
  }
}

@keyframes deleting {
  from {
    width: 100%;
  }
  to {
    width: 0;
  }
}

@keyframes blinking {
  0% {
    border-right-color: transparent;
  }
  50% {
    border-right-color: rgb(66, 65, 65);
  }
  100% {
    border-right-color: transparent;
  }
}

@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
    opacity: 0;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.dropdown {
  padding: 8px 0 8px 0;
  position: relative;
  height: fit-content;
  max-height: 200px;
  width: 100%;
  top: 8px;
  overflow-y: scroll;
  overflow-x: hidden;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  scroll-behavior: smooth;
}

.dropdown::-webkit-scrollbar {
  width: 6px;
  height: 0px;
  display: none;
}
.dropdown::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.dropdown:hover::-webkit-scrollbar {
  display: block;
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 0;
  width: 100%;
  margin: 0;
  cursor: pointer;
  color: $dark-black-blue;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-weight: 400;
  font-size: 13px;
  z-index: 2300;

  p {
    margin: 0;
  }

  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }

  &:hover {
    opacity: 0.7;
  }
}

.switcher {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  background-color: $off-white;
  border: 1px solid $off-white;
  border-radius: 6px;
  padding: 4px 0;
  margin-top: -2px;
  // width: 300px;
  @media only screen and (max-width: 600px) {
    margin-top: 0;
  }
}
.switch-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  border-radius: 6px;
  width: 100%;
  margin: 0 2px;
  cursor: pointer;
  color: $mid-gray;
  white-space: nowrap;
  font-weight: 400;
  font-size: 12px;
  img {
    filter: invert(63%) sepia(10%) saturate(617%) hue-rotate(200deg) brightness(93%) contrast(94%);
    margin-right: 8px;
  }
}

.activeswitch {
  background-color: white;
  padding: 4px 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  img {
    filter: none;
  }
}

.relative {
  position: relative;
}
.absolute {
  position: absolute;
}
.regenerate-article {
  // background-color: red;
  // bottom: 0;
  // right: 16px;
  margin-top: 1rem;
}

.slide-fade-enter-active {
  transition: all 0.2s ease-in;
}

.slide-fade-leave-active {
  transition: all 0.1s ease-out;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(100px);
}
.neg-margin {
  margin-left: -8px;
}

.templates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: 8px;
  left: 45%;
  font-size: 12px;
  background: $dark-green;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 2000;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.templates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $dark-green;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.redTemplates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: -140px;
  left: 16px;
  font-size: 12px;
  background: $coral;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 5000;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.redTemplates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $coral;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.greenTemplates {
  display: block;
  width: fit-content;
  height: 40px;
  position: absolute;
  top: -140px;
  left: 16px;
  font-size: 12px;
  background: $dark-green;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  pointer-events: none;
  line-height: 1.5;
  z-index: 5000;

  p {
    margin-top: 8px;
    padding: 0;
  }
}

.greenTemplates::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: $dark-green;
  bottom: -3px;
  left: 45%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.typed-deleted {
  overflow: hidden;
  white-space: nowrap;
  width: 0;
  animation: typing 2.5s steps(30, end) forwards, deleting 2.75s steps(30, end) 2.75s forwards,
    blinking 1s infinite;
  border-right: 1px solid;
}

.typed {
  display: flex;
  align-items: center;
  flex-direction: row;
  overflow: hidden;
  white-space: nowrap;
  width: 0;
  animation: typing 2s steps(30, end) forwards, blinking 1s infinite;
  // border-right: 1px solid;
}

@keyframes rotation {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(359deg);
  }
}

.rotate {
  animation: rotation 2.25s infinite linear;
  cursor: not-allowed;
}

.neg-l-mar {
  margin-left: -1rem;
}

.neg-lmar {
  margin-left: -1rem;
}

.summary-load-text {
  font-family: $thin-font-family;
  font-size: 14px;
  margin-left: 8px;
}

.invert {
  filter: invert(70%);
}

.invert-dark-blue {
  filter: invert(22%) sepia(51%) saturate(390%) hue-rotate(161deg) brightness(92%) contrast(87%);
}
.inverted {
  filter: invert(100%);
}

// .img-border {
//   border: 1px solid #416177;
//   border-radius: 100%;
//   padding: 0px 4px;
//   margin-left: 8px;
//   cursor: pointer;
//   img {
//     margin: 0 !important;
//     filter: invert(33%) sepia(27%) saturate(676%) hue-rotate(161deg) brightness(95%) contrast(84%);
//   }
// }

// .img-border:hover {
//   background: #416177;

//   img {
//     filter: invert(100%);
//   }
// }

.loader-container {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  margin-left: -48px;
  margin-bottom: 16px;
}

.loader-row {
  border-radius: 6px;
  padding: 0.25rem 0;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 6px;
  padding: 1.5rem 0.75rem;
}
.mar-top {
  margin-top: 24px;
}
.pad-btm {
  padding-bottom: 16px;
}

.dot {
  width: 4px;
  height: 4px;
  margin: 0 5px;
  background: rgb(97, 96, 96);
  border-radius: 50%;
  animation: bounce 1.2s infinite ease-in-out;
}

.dot:nth-child(2) {
  animation-delay: -0.4s;
}

.dot:nth-child(3) {
  animation-delay: -0.2s;
}

.search-text {
  color: $dark-black-blue;
  font-weight: 900;
  color: #6b6b6b;
}

::placeholder {
  color: $mid-gray;
}

button:disabled {
  background-color: $off-white !important;
  border: 1px solid rgba(0, 0, 0, 0.2) !important;
  cursor: not-allowed !important;
  opacity: 0.7;
}

.primary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: none;
  img {
    filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.lightblue-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 0.5px solid $dark-black-blue;
  color: $dark-black-blue;
  background-color: $white-blue;
  margin-right: 1rem;
  img {
    // filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-left: 8px;
  }
}

.tertiary-button {
  @include dark-blue-button();
  padding: 8px 12px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  margin-right: -2px;
  svg,
  img {
    // filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
  @media only screen and (max-width: 600px) {
    font-size: 10px;
  }
}

.secondary-button {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  background-color: white;
  padding: 8px 12px;
  img {
    filter: invert(25%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.no-hover-effect:hover {
  scale: 1;
  box-shadow: none;
  opacity: 0.5;
  cursor: not-allowed;
}

.toggle-type {
  cursor: pointer;
  p {
    padding: 0;
    margin: 0;
    font-weight: 400;
    font-size: 13px;
    color: $dark-black-blue;
  }

  img {
    filter: invert(40%);
    margin-left: 8px;
  }
}

.white-img {
  filter: invert(100%);
  margin-bottom: -16px;
  margin-left: 8px;
}

.row {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.row-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.column {
  flex-direction: column;
  height: 100%;
}

.news-column {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  padding: 0 64px;
}

.fullHeight {
  // margin-top: -10vh;
}

.center {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  button:first-of-type {
    margin-right: 1rem;
    @media only screen and (max-width: 600px) {
      margin-right: 0.25rem;
    }
  }
}
.area-container {
  @media only screen and (max-width: 600px) {
    // width: 50%;
    width: 80vw;
  }
  @media only screen and (max-width: 350px) {
    // width: 30%;
  }
}

.dim {
  opacity: 0.7;
}

.input-container {
  flex-wrap: nowrap;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0.75rem 1.2rem;
  border-radius: 6px;
  width: 50%;
  background-color: $offer-white;
  color: $base-gray;
  position: relative;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}

.article-container {
  position: relative;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: white;
  padding: 32px 24px;
  margin-bottom: 32px;
  border-radius: 4px;
  width: 50%;
  max-height: 100px;
  overflow-y: auto;
  scroll-behavior: smooth;

  &__empty {
    color: $mid-gray;
  }
}

.article-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}

.article-container::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.article-container:hover::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.clip-photo {
  height: 32px;
  width: 32px;
  object-fit: cover;
  cursor: text;
  margin-right: 8px;

  &:hover {
    opacity: 0.7;
  }
}

.article-text {
  display: flex;
  align-items: flex-start;
  font-size: 12px;
  color: $dark-black-blue;
  margin-bottom: 12px;
}

.s-padding {
  padding: 0 0.25rem !important;
}
.area-input-outline {
  width: 300px;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  padding: 5px 8px;
  border-radius: 4px;
  line-height: 1.75;
  border: 1px solid rgba(0, 0, 0, 0.1);
  outline: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family;
  font-weight: 400;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  margin-right: 1rem;
  resize: none;
}

.full-width {
  width: 100%;
}

.wider {
  width: 100%;
}

.area-input-small {
  width: 80%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.area-input-smallest {
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 0.5rem 0 0;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 13px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
  cursor: pointer;
}

.area-input-smallest:last-of-type {
  padding-left: 0.5rem;
}

.area-input {
  width: 100%;
  background-color: $offer-white;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.75;
  outline: none;
  border: none;
  letter-spacing: 0.5px;
  font-size: 14px;
  font-family: $thin-font-family !important;
  font-weight: 400;
  border: none !important;
  resize: none;
  text-align: left;
  overflow: auto;
  scroll-behavior: smooth;
  color: $dark-black-blue;
}

.area-input:disabled {
  cursor: not-allowed;
}

.twitter-blue {
  filter: invert(49%) sepia(87%) saturate(1104%) hue-rotate(175deg) brightness(95%) contrast(101%);
  margin-left: 8px;
}
.area-input::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.area-input::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.area-input::placeholder {
  font-family: $thin-font-family;
}

// .text-area-input {
//   line-height: 98.5px !important;
// }

.text-area-input {
  padding-top: 1.5rem;
}
.input-row {
  display: flex;
  align-items: center;
  flex-direction: row;
}

.input-row-start {
  display: flex;
  align-items: center;
  flex-direction: row;

  img,
  small {
    margin-top: 4px;
  }
}

.main-text {
  min-width: 80px !important;
  display: flex;
  flex-direction: row;
  align-items: center;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  margin: 0;
  font-size: 13px;
  color: $dark-black-blue;
  svg,
  img {
    filter: invert(40%);
    margin: 0;
    padding: 0;
  }
}

.main-text-img {
  flex-direction: row;
  align-items: center;
  justify-content: center;
  border-right: 1px solid rgba(0, 0, 0, 0.1);
  filter: invert(40%);
  margin: 0;
  padding-right: 1rem;
}

.neg-mar-btm {
  margin-bottom: -6px !important;
}

.main-slot {
  width: 28px;
  height: 28px;
  border-radius: 100%;
  // background-color: $dark-black-blue;
  background-color: $white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;

  img {
    // filter: invert(99%);
    filter: invert(20%) sepia(94%) saturate(234%) hue-rotate(161deg) brightness(92%) contrast(86%);
    margin: 0;
    padding: 0;
  }
}

.slot-container {
  margin-top: 16px;
  display: flex;
  align-items: center;
  flex-direction: column;
}

.empty-slot {
  border-radius: 100%;
  height: 10px;
  width: 10px;
  margin: 8px 0;
  background-color: rgba(108, 106, 106, 0.1);
}

.floating-action-bar {
  background-color: white;
  position: fixed;
  z-index: 3000;
  right: 0;
  top: 0;
  height: 100vh;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
  // width: 34px;
  width: 24px;
  display: flex;
  padding: 4px 0 8px 0;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.main-content {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: white;
  position: relative;
  border-radius: 8px;
  padding: 58px 36px 0 36px;
  height: fit-content;
  width: 100vw;
  color: $dark-blue;
  overflow-y: scroll;
  font-family: $thin-font-family;
  @media only screen and (max-width: 600px) {
    padding: 12px 12px 0 12px;
  }
}

.main-header {
  background-color: $dark-black-blue;
  color: white;
  width: 100.5vw;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0 !important;
}

.suggestions {
  position: absolute;
  bottom: 1rem;
  z-index: 2100;
  right: 1.5rem;
}

.pre-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.blue-bg {
  background-color: $white-blue;
  padding: 16px;
  border-radius: 4px;
}
.blue-icon {
  filter: invert(92%) sepia(53%) saturate(2928%) hue-rotate(178deg) brightness(72%) contrast(96%);
}

.img-highlight {
  filter: invert(40%);

  &:hover {
    filter: none;
  }
}

.right-mar {
  margin-right: 12px;
}
.loaded-content {
  width: 100%;
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
}

.wbbackground {
  background-color: $white-blue;
}

.loader-bg {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  // background-color: $white-blue;
  @media only screen and (max-width: 600px) {
    width: 70%;
  }
}

.no-content {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;

  width: 700px;
  @media only screen and (max-width: 600px) {
    width: 100vw;
  }
}

.title-row {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 14px;
  // margin-bottom: 1rem;
  img {
    margin-right: 1rem;
  }
  @media only screen and (max-width: 350px) {
    display: flex;
    justify-content: center;
    div {
      width: 55%;
      p {
        overflow: visible;
        text-align: center;
        white-space: normal;
      }
      // text-overflow: ;
    }
  }
}
.display-flex {
  display: flex;
}
.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;

  h1 {
    padding: 0;
    margin: 0;
  }
  p {
    margin: 8px 0;
  }
}

.space-between-evenly {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}
.remove {
  color: #6b6b6b;
  cursor: pointer;
  border-radius: 100%;
  padding: 1px 6px;
  margin-right: -4px;
  font-family: $thin-font-family;
  &:hover {
    color: $coral;
    background-color: $light-red;
  }
}
.logo {
  height: 20px;
}
.card-container {
  border-left: 1px solid $soft-gray;
  margin-left: 1rem;
  padding-left: 1rem;
  height: 75vh;
  overflow-y: auto;
}
.card {
  border: 1px solid $soft-gray;
  border-radius: 8px;
  box-shadow: 2px 2px 5px 0 $soft-gray;
  transition: all 0.3s;
  margin-bottom: 1rem;
  margin-right: 1rem;
}
.card:hover {
  transform: scale(1.025);
  box-shadow: 4px 4px 5px 0px $soft-gray;
}
.highlights-summary-container {
  border-bottom: 1px solid $soft-gray;
  height: 65vh;
  overflow-y: auto;
  padding: 0 1rem;
}
.summary-buttons-container {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
}
.summary-button {
  @include gray-text-button();
  margin: 0 0.5rem;
  padding: 8px 16px;
  img {
    height: 12px;
    margin-right: 0.5rem;
  }
}

.divider {
  position: relative;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

.divider-text {
  position: absolute;
  top: -32px;
  left: 44%;
  z-index: 20;
  background-color: white;
  padding: 4px 16px;
  border-radius: 20px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  @media only screen and (max-width: 600px) {
    left: 31.5%;
  }
}

.summaries-container {
  position: relative;
  display: flex;
  justify-content: flex-start;
  width: 100vw;
  margin-bottom: 0;
  background-color: $off-white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 0 32px 32px 32px;
}
.clips-container {
  padding-top: 16px;
  display: flex;
  justify-content: flex-start;
  width: 100%;
  background-color: white;
  // margin-top: 40px;
}
.label-width {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  height: fit-content;
  img {
    margin: 0;
    padding: 0;
    margin-right: 8px;
  }
}
.content-width {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  overflow-y: auto;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
  overflow: none;
  text-overflow: ellipsis;
  margin-bottom: 2rem;
  @media only screen and (max-width: 600px) {
    height: 240px;
    gap: 4px;
    flex-direction: column-reverse;
    margin-bottom: 0;
  }
}

.news-container {
  // padding-top: 32px;
  // width: 50%;
  padding: 8px 16px 0px 16px;
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  @media only screen and (max-width: 600px) {
    width: 90%;
    padding-top: 48px;
  }
}

.news-container-med {
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  @media only screen and (max-width: 600px) {
    width: 90%;
    // padding-top: 48px;
  }
}

.no-results {
  display: flex;
  align-items: center;
  justify-content: center;

  font-weight: 400;
  font-size: 13px;
  color: #6b6b6b;
}

.title-container {
  position: relative;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}

.back {
  position: absolute;
  display: flex;
  align-items: center;
  justify-content: center;
  top: 0.75rem;
  left: -56px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 100%;
  padding: 3px 2px;
  cursor: pointer;

  img {
    filter: invert(40%);
  }
  @media only screen and (max-width: 600px) {
    left: 50%;
    top: -2rem;
  }
}

.title-bar {
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding: 16px 0 24px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.sub-text {
  color: $light-gray-blue;
  margin: 8px 0;
  font-size: 14px;
  font-family: $thin-font-family;

  span {
    font-weight: 200;
    word-wrap: break-word;
  }
  @media only screen and (max-width: 600px) {
    text-align: center;
  }
}

.no-text-margin {
  margin: 0;
  @media only screen and (max-width: 600px) {
    text-align: center;
  }
}

.author {
  display: inline-block;
  overflow: hidden;
  white-space: nowrap;
  max-width: 200px;
  min-height: 22px;
  text-overflow: ellipsis;
  background-color: $soft-gray;
  padding: 4px 12px;
  color: $base-gray;
  border-radius: 12px;
  @media only screen and (max-width: 600px) {
    max-width: 65px;
    font-size: 10px !important;
  }
}

.off-gray {
  color: #6b6b6b;
}

.news-card {
  position: relative;
  min-height: 220px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 1rem 0;
  margin-bottom: 1rem;
}

.news-card-medium {
  position: relative;
  min-height: 200px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 0 0 1rem 0;
  margin-bottom: 1rem;

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    height: 60px;
    overflow: none;
    text-overflow: ellipsis;
    margin-bottom: 8px;
    @media only screen and (max-width: 600px) {
      align-items: flex-start;
      margin-left: 0.25rem;
    }
  }
}

.card-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  @media only screen and (max-width: 600px) {
    padding-top: 1rem;
  }
}

.card-row-med {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  img {
    height: 20px;
    margin-right: 0.5rem;
  }
}
.card:hover {
  transform: scale(1.025);
}
.card-top-left {
  display: flex;
  font-size: 12px;
  img {
    height: 12px;
    margin-right: 0.5rem;
  }
}
.cover-photo {
  height: 112px;
  width: 116px;
  margin-left: 0.5rem;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: pointer;

  &:hover {
    opacity: 0.7;
  }
  @media only screen and (max-width: 600px) {
    margin-left: 0.25rem;
    // height: 112px;
    // width: 224px;
    width: 100%;
    object-fit: cover;
    // height: 50%;
  }
}

.cover-photo-no-l-margin {
  height: 112px;
  width: 116px;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;
}

.small-photo {
  height: 28px;
  width: 28px;
  margin-bottom: 8px;
  object-fit: cover;
  cursor: text;
  border-radius: 100%;
}

.ellipsis-text {
  max-width: 520px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.grow:hover {
  transform: scale(1.2);
  box-shadow: 2px 4px 32px rgba($color: $black, $alpha: 0.3);
  opacity: 0.7;
}
.grow {
  transition: all 0.2s;
}

.shadow-hover:hover {
  // transform: scale(1.01);
  // padding: 2px;
  opacity: 0.5;
}
.shadow-hover {
  transition: all 0.1s;
}

.ellipsis-text-small {
  max-width: 60px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
}

.article-title {
  font-size: 16px;
  font-weight: 900;
  line-height: 24px;
  letter-spacing: 0;
  color: $base-gray;
  margin: 12px 0;
  max-width: 500px;
  white-space: nowrap;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  cursor: pointer;

  &:hover {
    color: #6b6b6b;
  }
  @media only screen and (max-width: 600px) {
    font-size: 12px;
    max-width: 270px;
  }
}

.article-preview {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  height: 68px;
  line-height: 24px;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;
}

.article-preview-medium {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  line-height: 24px;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;
}
.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  margin-top: 1rem;
  @media only screen and (max-width: 600px) {
    margin-top: 0rem;
  }
  span {
    font-size: 12px;
    margin-right: 0.5rem;
    @media only screen and (max-width: 600px) {
      margin-right: 0.25rem;
    }
  }
}
.footer-icon-container {
  display: flex;
  align-items: center;
}
.right-arrow-footer {
  padding: 2px 0;
  height: 20px;
  margin-left: 1rem;
  cursor: text;
}
.left-mar {
  margin-left: 1rem;
}
.footer-icon {
  height: 24px;
  margin-left: 1rem;
  cursor: pointer;
}
.author-time {
  display: flex;
  align-items: center;
  color: $light-gray-blue;
}
.time {
  @media only screen and (max-width: 600px) {
    max-width: 100px;
    font-size: 10px !important;
  }
}
.divier-dot {
  position: relative;
  bottom: 0.2rem;
}
.large-dot {
  font-size: 40px;
  bottom: 1.7rem;
  margin-right: 0.75rem;
}
.regen-header {
  display: flex;
  justify-content: space-between;
  border-bottom: 1px solid $soft-gray;
  margin-bottom: 1rem;
}
.paid-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.regen-header-title {
  margin: 0.25rem 0;
}
.regen-header-subtitle {
  font-size: 12px;
  color: $light-gray-blue;
  margin: 0.5rem 0;
}
.regen-body {
  margin: 0.5rem 0;
  border-bottom: 1px solid $soft-gray;
}
.paid-body {
  margin: 0.5rem 0;
}
.regen-body-title {
  margin: 0 0 0 0;
}
.padding {
  padding: 1rem 0;
}
.regen-body-text {
  resize: none;
  outline: none;
  border: 1px solid $soft-gray;
  border-radius: 8px;
  height: 4rem;
  width: 500px;
  overflow-y: auto;
  margin: 1rem 0;
  padding: 1rem;
  font-family: $thin-font-family !important;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}
.regen-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 16px;
  padding-bottom: 8px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.paid-title {
  margin-top: 0;
  margin-bottom: 2rem;
}
.paid-footer {
  position: sticky;
  background: white;
  width: 100%;
  bottom: 0;
  padding-top: 16px;
  padding-bottom: 8px;
  margin: 1rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.blue-border-button {
  @include dark-blue-border-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  width: 8rem;
  margin-bottom: 1rem;
}
.cancel-button {
  @include gray-text-button();
  &:hover {
    scale: 1;
    opacity: 0.7;
    box-shadow: none;
  }
}
.save-button {
  @include dark-blue-button();
  &:hover {
    scale: 1;
    opacity: 0.9;
    box-shadow: none;
  }
  margin-left: 0.5rem;
}
.pointer {
  cursor: pointer;
}
.regen-modal {
  margin-top: 84px;
}
.paid-modal {
  margin-top: 132px;
  font-family: $thin-font-family;
}
.regen-container {
  width: 500px;
  max-height: 500px;
  position: relative;
  overflow-y: scroll;
  font-family: $thin-font-family;
  @media only screen and (max-width: 600px) {
    width: 100%;
  }
}
::v-deep .modal {
  @media only screen and (max-width: 600px) {
    width: 90%;
  }
}
.message-text {
  font-family: $thin-font-family !important;
  word-wrap: break-word;
  white-space: pre-wrap;
}
@keyframes shimmer {
  100% {
    -webkit-mask-position: left;
  }
}

.shimmer {
  display: inline-block;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
}

.gray-text {
  color: $mid-gray;
  font-family: $thin-font-family;
}

.small-text {
  font-family: $thin-font-family;
  color: $mid-gray;
  font-weight: 400;
  font-size: 13px;
}

.loadingText {
}

.article-preview-skeleton {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: space-between;
  padding: 20px;
  border-radius: 4px;
  margin-top: 16px;
  width: 100%;
}

.summary-preview-skeleton {
  display: flex;
  justify-content: center;
  width: 100%;
  padding: 8px 0;
  border-radius: 6px;
  flex-direction: column;
  @media only screen and (max-width: 600px) {
    min-width: 0;
  }
}

.thumbnail {
  height: 112px;
  width: 116px;
  background-color: #f2f2f2;
  border-radius: 6px;
  margin-left: 16px;
}

.content {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.title {
  width: 100%;
  min-width: 400px;
  height: 24px;
  background-color: #f2f2f2;
  margin-bottom: 8px;
  border-radius: 6px;
}
.title-wide {
  width: 100%;
  height: 28px;
  background-color: $dark-black-blue;
  margin-bottom: 12px;
  border-radius: 12px;
}

.meta {
  width: 100%;
  min-width: 399px;
  height: 8px;
  background-color: #f2f2f2;
  border-radius: 6px;
  margin-bottom: 8px;
}

.blue-logo {
  filter: brightness(0%) invert(26%) sepia(16%) saturate(936%) hue-rotate(162deg) brightness(93%)
    contrast(97%);
}

.meta-wide {
  width: 100%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shorter {
  width: 80%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-shortest {
  width: 60%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}
.meta-small {
  width: 40%;
  height: 16px;
  background-color: $black-blue;
  border-radius: 8px;
  margin-bottom: 8px;
}

.bold-text {
  font-weight: bold;
  color: $base-gray;
  font-size: 12px;

  span {
    color: #6b6b6b;
  }
}

.skeleton-bar {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  padding: 16px 0;
}

.skeleton-button {
  height: 20px;
  width: 100px;
  margin-right: 16px;
  background-color: #f2f2f2;
  border-radius: 6px;
}

.skeleton-icon {
  border-radius: 50%;
  height: 20px;
  width: 20px;
  background-color: #f2f2f2;
}

.excerpt {
  width: 100%;
  min-width: 399px;
  height: 8px;
  background-color: #f2f2f2;
  border-radius: 6px;
}
.excerpt-wide {
  width: 100%;
  height: 8px;
  background-color: #f2f2f2;
  margin-top: 16px;
  border-radius: 6px;
}

.skeleton-footer {
  width: 150px;
  height: 12px;
  margin-top: 32px;
  background-color: #f2f2f2;
  border-radius: 6px;
}

.wrapper {
  display: flex;
  align-items: center;
  // background-color: ;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip {
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -12px;
  margin-bottom: 15px;
  opacity: 0;
  padding: 8px;
  pointer-events: none;
  position: absolute;
  width: 100px;
  -webkit-transform: translateY(10px);
  -moz-transform: translateY(10px);
  -ms-transform: translateY(10px);
  -o-transform: translateY(10px);
  transform: translateY(10px);
  -webkit-transition: all 0.25s ease-out;
  -moz-transition: all 0.25s ease-out;
  -ms-transition: all 0.25s ease-out;
  -o-transition: all 0.25s ease-out;
  transition: all 0.25s ease-out;
  -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
  box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28);
}

.tooltip-wide {
  width: 200px !important;
  left: -62px !important;
}

/* This bridges the gap so you can mouse into the tooltip without it disappearing */
.wrapper .tooltip:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-top: solid $dark-black-blue 10px;
  bottom: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip {
  display: none;
}

.lte8 .wrapper:hover .tooltip {
  display: block;
}

.red-text {
  color: $coral;
  font-weight: 400;
  font-size: 12px;
}

.slot-count {
  font-size: 11px;
  margin-top: 6px;
  opacity: 0.7;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: all 0.2s ease;
}
.slide-left-enter,
.slide-left-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
.slide-left-enter-to,
.slide-left-leave {
  transform: translateX(0);
  opacity: 1;
}
.article-copy-container {
  height: 20px;
  margin-top: 0.5rem;
}
.summarize-button {
  @media only screen and (max-width: 600px) {
    font-size: 11px;
    img {
      height: 11px;
    }
  }
}

.nav-text {
  font-weight: 400;
  font-family: $thin-font-family !important;
  color: #6b6b6b;
  font-size: 13px;
  padding: 6px 0;
  @media only screen and (max-width: 600px) {
    padding: 14px 0;
    color: $dark-black-blue;
    // font-size: 18px;
  }
  img {
    margin-left: 8px;
  }
}

.content-dropdown {
  width: 260px;
  position: absolute;
  top: 150px;
  left: auto;
  font-size: 13px;
  font-weight: 400;
  background: white;
  padding: 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 1000;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    padding: 8px 16px;
    color: #7c7b7b;
    cursor: pointer;
    width: 245px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin: 0;
  }

  p:hover {
    color: $dark-black-blue;
  }
}

.search-dropdown {
  width: 260px;
  position: absolute;
  top: 40px;
  right: -8px;
  font-size: 13px;
  font-weight: 400;
  background: white;
  padding: 0;
  border-radius: 5px;
  box-shadow: 0 11px 16px rgba(0, 0, 0, 0.1);
  line-height: 1.5;
  z-index: 1000;
  border: 1px solid rgba(0, 0, 0, 0.1);

  p {
    padding: 8px 16px;
    color: #7c7b7b;
    cursor: pointer;
    width: 245px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    margin: 0;
  }

  p:hover {
    color: $dark-black-blue;
  }
}

.searches-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}

.searches-container::-webkit-scrollbar-thumb {
  background-color: transparent;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.searches-container:hover::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.searches-container {
  max-height: 300px;
  overflow-y: scroll;
  scroll-behavior: smooth;
  // margin-bottom: 1rem;
  padding: 1rem 0;
  @media only screen and (max-width: 600px) {
    font-size: 13px;
    p {
      margin-left: 0.5rem;
    }
  }
}

.input {
  position: sticky;
  z-index: 5010;
  top: 1.5rem;
  width: 224px;
  margin: 1.5rem 0 0.5rem 1rem;
  border-radius: 20px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-family: $thin-font-family !important;
  background-color: white;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 8px 20px 8px 10px;
}

.search-input {
  border: none;
  outline: none;
  margin-left: 0.5rem;
  width: 100%;
}

.absolute-icon {
  position: absolute;
  padding-left: 4px;
  background: transparent;
  opacity: 0;
  right: 8px;
  cursor: pointer;
}

.dropdownBorder {
  color: white;
  border-radius: 4px;
  background-color: $dark-black-blue;
  font-size: 12px;
  padding: 8px;
  // @media only screen and (max-width: 600px) {
  //   padding: 16px 8px 48px 8px;
  // }
}

.rotate-img {
  transform: rotate(180deg);
}

.absolute-right {
  position: absolute;
  right: 8px;
  top: -48px;
}

.absolute-right-bottom {
  position: absolute;
  right: 0;
  bottom: 0;
}

.absolute-left {
  position: absolute;
  left: 16px;
  top: 16px;
}

.blue-filter {
  filter: invert(61%) sepia(69%) saturate(4249%) hue-rotate(204deg) brightness(100%) contrast(104%);
}

.circle-border {
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 100%;
  padding: 5px 6px;
  background-color: $white-blue;
  img {
    margin: 0 !important;
  }
}

.transparent-bg {
  background: transparent;
}

.white-bg {
  background: white;
}

.modal {
  position: fixed;
  z-index: 1;
  left: 0;
  top: 0;
  width: 100%;
  height: 100%;
  overflow: auto;
  background-color: rgba(0, 0, 0, 0.4);
}

.modal-content {
  background-color: #fefefe;
  margin: 15% auto;
  padding: 20px;
  border: 1px solid #888;
  width: 70%;
}

.close {
  color: #aaa;
  float: right;
  font-size: 28px;
  font-weight: bold;
}

.close:hover,
.close:focus {
  color: black;
  text-decoration: none;
  cursor: pointer;
}

.danger {
  cursor: pointer;
  filter: invert(40%);
  position: absolute;
  right: 0;
  margin-right: -8px;
  &:hover {
    opacity: 0.7 !important;
    filter: invert(51%) sepia(74%) saturate(2430%) hue-rotate(320deg) brightness(104%)
      contrast(121%) !important;
  }
}
.attachment-header-container {
  @media only screen and (max-width: 600px) {
    display: flex;
    flex-direction: column-reverse;
  }
}
.tweet-attachement {
  img {
    @media only screen and (max-width: 600px) {
      width: 80vw;
    }
  }
  video {
    @media only screen and (max-width: 600px) {
      width: 80vw;
    }
  }
}
.reports-lip-container {
  position: fixed;
  // top: 535%;
  top: 50%;
  right: 484px;
  z-index: 5500;
  cursor: pointer;
}
.reports-lip-closed {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $offer-white;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 6px;
  margin-right: 24px;
  cursor: pointer;
  box-shadow: 1px 1px 10px 1px rgba(0, 0, 0, 0.1);

  img {
    transform: rotate(180deg);
  }
  transition: all 0.2s;
}

.added-clip {
  transform: scale(1.2);
  background-color: $dark-black-blue;

  img {
    filter: invert(100%);
  }
}

.reports-lip {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: $offer-white;
  border-radius: 50%;
  border: 1px solid rgba(0, 0, 0, 0.1);
  padding: 6px;
}
.reports-lip-container-bar {
  position: absolute;
  top: 80px;
  right: 32px;
  z-index: -1;
  cursor: pointer;
  width: 2.5rem;
}
.reports-lip-bar {
  display: flex;
  align-items: center;
  background-color: $white-blue;
  border-radius: 20px;
  border-left: 1px solid $white-blue;
  border-top: 1px solid $white-blue;
  border-bottom: 1px solid $white-blue;
  // height: 7rem;
  height: 4rem;
  z-index: -1;
}
.blue-box {
  background-color: $white-blue;
  height: 4rem;
  width: 21px;
  position: absolute;
  right: -1px;
  // border-left: 5px solid $white-blue;
}
.lip-img {
  height: 14px;
  padding: 0;
  margin: 0;
  z-index: 5500;
}
.flip {
  transform: rotate(180deg);
}
.reports-width-height {
  width: 500px;
  height: 100vh;
  overflow-y: auto;
  font-family: $thin-font-family;
  padding: 0 8px 0 16px;
  background-color: $offer-white;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
  position: fixed;
  z-index: 3000;
  right: 0;
  top: 0;
  box-shadow: 30px 30px 40px;
  @media only screen and (max-width: 600px) {
    width: 100vw;
  }
}
.summary-email-span {
  font-size: 12px;
  font-family: $thin-font-family !important;
}
.gen-content-button {
  // height: 2rem;
  margin-left: 1rem;
  width: 8.25rem;
}

.detail-column {
  display: flex;
  flex-direction: column;
}

.details {
  margin-left: 134px;
  padding-bottom: 8px;
  // border-bottom: 1px solid rgba(0, 0, 0, 0.1);

  button {
    max-width: 120px;
    padding: 6px;
    // margin-top: -8px;
    margin-right: 16px;
    border-radius: 3px;
    text-overflow: ellipsis;
    background-color: white;
    color: $dark-black-blue;
    border: 1px solid rgba(0, 0, 0, 0.1);
    font-family: $thin-font-family;
    font-size: 12px;
    display: flex;
    align-items: center;
    cursor: pointer;
  }
}

.details::-webkit-scrollbar {
  width: 0px;
  height: 6px;
  display: none;
}
.details::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.details:hover::-webkit-scrollbar {
  display: block;
}

.bottommargin {
  margin-bottom: 2rem;
}

.faded {
  filter: invert(55%);
}

input::-webkit-calendar-picker-indicator {
  margin-left: -8px;
}

input[type='date']::-webkit-input-placeholder {
  margin-left: -8px;
  // visibility: hidden !important;
}

.filtered-blue {
  filter: invert(20%) sepia(28%) saturate(811%) hue-rotate(162deg) brightness(94%) contrast(81%);
}
</style>