<template>
  <div class="search">
    <Modal v-if="promptModalOpen" class="paid-modal">
      <div class="regen-container">
        <div style="background-color: white" class="paid-header sticky-header">
          <div>
            <h3 class="regen-header-title">Popular Prompts</h3>
            <p class="regen-header-subtitle"></p>
          </div>
          <div class="pointer" @click="togglePromptModal"><small>X</small></div>
        </div>
        <div class="paid-body">
          <div>
            <div class="paid-center aligned-left">
              <p
                class="paid-item"
                @click="selectPrompt(prompt)"
                v-for="(prompt, i) in searchSuggestions"
                :key="i"
              >
                {{ prompt }}
              </p>
            </div>
          </div>
        </div>
        <div class="paid-footer">
          <div class="row">
            <div
              style="padding-top: 9px; padding-bottom: 9px"
              class="cancel-button"
              @click="togglePromptModal"
            >
              Close
            </div>
          </div>
        </div>
      </div>
    </Modal>

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
              {{ contentLoading ? 'submitting' : 'submit' }}
              <div style="margin-left: 4px" v-if="contentLoading" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Modal>

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
                style="width: 100%; margin-top: 0.5rem"
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
              {{ savingAlert ? 'Submitting' : 'Submit' }}
              <div style="margin-left: 4px" v-if="savingAlert" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Modal>

    <Modal v-if="saveModalOpen" class="regen-modal">
      <div :class="{ dim: savingSearch }" class="regen-container">
        <div class="paid-header">
          <div>
            <h3 class="regen-header-title">Save</h3>
            <p class="regen-header-subtitle">Save your current search</p>
          </div>
          <div @click="toggleSaveModal" class="pointer"><small>X</small></div>
        </div>

        <div class="paid-body">
          <label style="font-size: 13px" for="detail-title">Name:</label>
          <input
            id="detail-title"
            style="width: 100%; margin: 0.5rem 0 1rem 0"
            class="area-input-outline"
            type="text"
            placeholder="Name your search"
            v-model="searchName"
          />
        </div>

        <div style="margin: 0; padding-bottom: 0" class="paid-footer aligned-right">
          <div class="row">
            <button :disabled="savingSearch" @click="toggleSaveModal" class="cancel-button">
              Cancel
            </button>
            <button @click="createSearch" :disabled="savingSearch" class="save-button">
              {{ savingSearch ? 'Saving' : 'Save' }}
              <div style="margin-left: 4px" v-if="savingSearch" class="loading-small">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </Modal>
    <section id="clips" class="container">
      <div class="header centered sticky-top padding-top col">
        <div
          style="width: 100%; margin-top: 0.5rem"
          v-if="selectedSearch && !loading"
          class="space-between horizontal-padding"
        >
          <p
            v-if="mainView !== 'website' && mainView !== 'instagram'"
            class="sub-text ellipsis-text"
            style="margin: 16px 0"
          >
            <span :title="booleanString">{{
              booleanString ? booleanString.replace('lang:en', '') : ''
            }}</span>
          </p>
          <p
            v-else-if="mainView === 'instagram'"
            class="sub-text ellipsis-text"
            style="margin: 16px 0"
          >
            <span :title="newSearch">{{ newSearch }}</span>
          </p>
          <p v-else style="margin: 16px 0" class="sub-text">Article Report</p>

          <p style="margin-right: 6px; padding-bottom: 0">
            {{
              mainView === 'news'
                ? `${filteredArticles.length} News Clips`
                : mainView === 'website'
                ? '1 Article'
                : mainView === 'instagram'
                ? `${posts.length} Posts`
                : `${tweets.length} Tweets`
            }}
          </p>
          <!-- v-if="
              (filteredArticles && filteredArticles.length) ||
              (tweets && tweets.length) ||
              addedArticles.length ||
              posts.length
            " -->
        </div>
      </div>

      <div
        :class="
          selectedSearch &&
          !loading &&
          !(
            (filteredArticles && filteredArticles.length) ||
            (tweets && tweets.length) ||
            addedArticles.length
          )
            ? 'extra-padding-top'
            : ''
        "
        class="content-body"
        style="width: 100%"
      >
        <div v-if="mainView === 'news'">
          <div style="padding-top: 2rem" v-if="!(filteredArticles && filteredArticles.length)">
            <div style="margin-top: -0.5rem" v-if="loading">
              <div class="small-container centered">
                <div class="loading">
                  <p>Generating clips</p>
                  <div class="dot"></div>
                  <div class="dot"></div>
                  <div class="dot"></div>
                </div>
              </div>
            </div>

            <div
              style="width: 100%; padding: 0 32px; padding-top: 16px"
              v-else
              class="small-container letter-spacing"
            >
              <div v-if="!selectedSearch" class="text-width">
                <p style="margin: 0">Get a pulse on whats happening in the news</p>
              </div>

              <div style="width: 100%; margin-top: 32px">
                <div style="width: 100%" class="large-input-container">
                  <div style="border: none; box-shadow: none" class="input-container">
                    <img
                      class="left-margin-m"
                      src="@/assets/images/search.svg"
                      height="20px"
                      alt=""
                    />
                    <textarea
                      v-if="mainView !== 'website'"
                      id="search-input"
                      @keyup.enter="generateNewSearch(false)"
                      class="area-input text-area-input"
                      placeholder="Search..."
                      autocomplete="off"
                      v-model="newSearch"
                      v-autoresize
                      :disabled="
                        loading ||
                        summaryLoading ||
                        (mainView === 'social' && !hasTwitterIntegration) ||
                        (mainView === 'instagra,' && !hasIgIntegration)
                      "
                    />

                    <textarea
                      v-else
                      @keyup.enter="uploadArticle"
                      class="area-input text-area-input"
                      placeholder="Paste article url..."
                      v-model="uploadLink"
                      :disabled="contentLoading"
                    />
                    <!-- <div
                    v-if="mainView === 'news'"
                    @click="toggleDateDropdown"
                    class="image-container-blue left-margin wrapper"
                  >
                    <img
                      style="filter: invert(100%)"
                      src="@/assets/images/calendar.svg"
                      height="14px"
                      alt=""
                    />
                    <div class="tooltip">Date Range</div>
                  </div>
                  <div class="right-margin" v-else></div> -->

                    <!-- <div v-if="dateOpen" class="date-dropdown">
                    <div class="space-between">
                      <small style="padding-top: 8px" class="gray-text">Date Range</small>

                      <small @click="toggleDateDropdown" class="close-x">X</small>
                    </div>

                    <div style="width: 100%; margin-top: 8px">
                      <input class="area-input-smallest" type="date" v-model="dateStart" />
                      -
                      <input class="area-input-smallest" type="date" v-model="dateEnd" />
                    </div>
                  </div> -->

                    <div
                      v-if="mainView !== 'website'"
                      @click="generateNewSearch(false)"
                      class="image-container left-margin wrapper"
                      :class="newSearch ? 'dark-blue-bg' : ''"
                    >
                      <img
                        style="margin: 0"
                        src="@/assets/images/paper-plane-top.svg"
                        height="14px"
                        alt=""
                      />

                      <div class="tooltip">Submit</div>
                    </div>

                    <div
                      v-else
                      @click="uploadArticle"
                      class="image-container left-margin wrapper"
                      :class="newSearch ? 'dark-blue-bg' : ''"
                    >
                      <img
                        style="margin: 0; cursor: text"
                        src="@/assets/images/paper-plane-top.svg"
                        height="14px"
                        alt=""
                      />

                      <div class="tooltip">Submit</div>
                    </div>
                  </div>

                  <div>
                    <div class="expanded-item">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/newspaper.svg" height="20px" alt="" />
                        <p>Source</p>
                      </div>

                      <div class="switcher">
                        <div
                          @click="switchMainView('news')"
                          :class="{ activeswitch: mainView === 'news' }"
                          class="switch-item"
                        >
                          News
                        </div>
                        <div
                          @click="switchMainView('social')"
                          :class="{ activeswitch: mainView === 'social' }"
                          class="switch-item"
                        >
                          X
                        </div>
                        <div
                          @click="switchMainView('instagram')"
                          :class="{ activeswitch: mainView === 'instagram' }"
                          class="switch-item"
                        >
                          IG
                        </div>
                        <div
                          @click="switchMainView('website')"
                          :class="{ activeswitch: mainView === 'website' }"
                          class="switch-item"
                        >
                          URL
                        </div>
                        <div
                          @click="switchMainView('pdf')"
                          :class="{ activeswitch: mainView === 'pdf' }"
                          class="switch-item"
                        >
                          PDF
                        </div>
                      </div>
                    </div>

                    <div class="expanded-item">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/calendar.svg" height="18px" alt="" />
                        <p>Date Range</p>
                      </div>

                      <div>
                        <input class="area-input-smallest" type="date" v-model="dateStart" />
                        -
                        <input class="area-input-smallest" type="date" v-model="dateEnd" />
                      </div>
                    </div>

                    <div class="expanded-item-column">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/arrow-trend-up.svg" height="18px" alt="" />
                        <p>Search Examples:</p>
                      </div>

                      <div class="horizontal-padding rows">
                        <p
                          v-for="(example, i) in searchExamples"
                          :key="i"
                          @click="setNewSearch(example)"
                          class="bold gray-title"
                        >
                          {{ example }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- <div class="no-margins">
                <p class="bold gray-title">Simple search</p>
                <p style="margin-bottom: 16px; margin-left: 4px">
                  <img src="@/assets/images/return.svg" height="11px" alt="" /> Lululemon,
                  "commercial real estate" AND technology, Apple no stock related news
                </p>
                <p class="bold gray-title">Question-based search</p>
                <p style="margin-bottom: 16px; margin-left: 4px">
                  <img src="@/assets/images/return.svg" height="11px" alt="" />
                  What is the sentiment around apple vision pro? List top journalist writing about
                  sustainability and fashion along with creative pitching angles.
                </p>
                <p class="bold gray-title">Date Range</p>
                <p style="margin-bottom: 16px; margin-left: 4px">
                  <img src="@/assets/images/return.svg" height="11px" alt="" />
                  The default is 7 days. Click calendar icon to adjust.
                </p>
                <p class="bold gray-title">New summary</p>
                <p style="margin-bottom: 16px; margin-left: 4px">
                  <img src="@/assets/images/return.svg" height="11px" alt="" />
                  Click the speech bubble in the right chatbar to see popular prompts.
                </p>
              </div> -->
            </div>
          </div>

          <div style="padding: 40px 0" ref="topDivider" v-else>
            <div
              style="margin: 2.75rem 0"
              v-for="article in filteredArticles"
              :key="article.id"
              class="news-container"
            >
              <div class="news-card" @click="selectArticle(article)">
                <header class="row-between">
                  <div class="card-col">
                    <div class="card-top-left">
                      <span>{{ article.source.name }}</span>
                    </div>
                    <h1 class="article-title" @click="goToArticle(article.link)">
                      {{ article.title }}
                    </h1>
                    <p class="article-preview">
                      {{ article.description }}
                    </p>
                  </div>
                  <img
                    @click="goToArticle(article.link)"
                    :src="article.image_url"
                    class="cover-photo"
                  />
                </header>

                <div class="card-footer">
                  <div class="author-time">
                    <span class="author">{{ article.author }}</span>
                    <span class="divider-dot">.</span>
                    <span class="off-gray time">{{
                      getTimeDifferenceInMinutes(article.publish_date)
                    }}</span>
                    <span class="divider-dot">.</span>
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
                        class="tertiary-button"
                        style="margin-left: 16px"
                        :disabled="
                          articleSummaryLoading || loading || summaryLoading || savingSearch
                        "
                      >
                        <img
                          v-if="loadingUrl !== article.link"
                          src="@/assets/images/sparkles-thin.svg"
                          height="14px"
                          alt=""
                        />
                        {{
                          articleSummaryLoading && loadingUrl === article.link
                            ? 'Summarizing'
                            : 'Summarize'
                        }}

                        <div
                          style="margin-left: 4px"
                          v-if="articleSummaryLoading && loadingUrl === article.link"
                          class="loading-small"
                        >
                          <div class="dot"></div>
                          <div class="dot"></div>
                          <div class="dot"></div>
                        </div>
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
                  <div class="relative">
                    <pre v-html="article.summary" class="pre-text blue-text-bg"></pre>
                    <div
                      @click="copyArticleSummary(article.summary)"
                      class="wrapper image-container top-right"
                    >
                      <img
                        style="cursor: pointer"
                        class="img-highlight"
                        src="@/assets/images/clipboard.svg"
                        height="12px"
                        alt=""
                      />
                      <div class="tooltip">{{ copyTip }}</div>
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

                      <div class="relative left-margin">
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
                          <div
                            style="margin-left: 4px"
                            v-else-if="contentLoading"
                            class="loading-small"
                          >
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                          </div>
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
                          {{
                            articleSummaryLoading && loadingUrl === article.link
                              ? 'Submitting'
                              : 'Submit'
                          }}
                          <div
                            style="margin-left: 4px"
                            v-if="articleSummaryLoading && loadingUrl === article.link"
                            class="loading-small"
                          >
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div v-else-if="mainView === 'social'">
          <div v-if="loading">
            <div class="small-container">
              <div class="loading">
                <p>Generating clips</p>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </div>
          </div>

          <div style="padding-top: 2rem" v-else-if="!(tweets && tweets.length)">
            <div
              style="width: 100%; padding: 0 32px; padding-top: 16px"
              class="small-container letter-spacing"
            >
              <div v-if="!selectedSearch" class="text-width">
                <p v-if="hasTwitterIntegration" style="margin: 0">
                  Get a pulse on whats happening on X (Twitter)
                </p>

                <p style="margin: 0" v-else>
                  Start by connecting your X account
                  <span class="link" @click="goToIntegrations">here</span>.
                </p>
              </div>

              <div style="width: 100%; margin-top: 32px">
                <div style="width: 100%" class="large-input-container">
                  <div style="border: none; box-shadow: none" class="input-container">
                    <img
                      class="left-margin-m"
                      src="@/assets/images/search.svg"
                      height="20px"
                      alt=""
                    />
                    <textarea
                      v-if="mainView !== 'website'"
                      id="search-input"
                      @keyup.enter="generateNewSearch(false)"
                      class="area-input text-area-input"
                      :placeholder="
                        hasTwitterIntegration
                          ? 'Enter keywords...'
                          : 'Connect your X account to search...'
                      "
                      autocomplete="off"
                      v-model="newSearch"
                      v-autoresize
                      :disabled="
                        loading ||
                        summaryLoading ||
                        (mainView === 'social' && !hasTwitterIntegration)
                      "
                    />

                    <textarea
                      v-else
                      @keyup.enter="uploadArticle"
                      class="area-input text-area-input"
                      placeholder="Paste article url..."
                      v-model="uploadLink"
                      :disabled="contentLoading"
                    />
                    <div
                      v-if="mainView !== 'website'"
                      @click="generateNewSearch(false)"
                      class="image-container left-margin right-margin-m wrapper"
                      :class="newSearch ? 'dark-blue-bg' : ''"
                    >
                      <img
                        style="margin: 0; cursor: text"
                        src="@/assets/images/paper-plane-top.svg"
                        height="14px"
                        alt=""
                      />

                      <div class="tooltip">Submit</div>
                    </div>

                    <div
                      v-else
                      @click="uploadArticle"
                      class="image-container left-margin right-margin-m wrapper"
                      :class="newSearch ? 'dark-blue-bg' : ''"
                    >
                      <img
                        style="margin: 0; cursor: text"
                        src="@/assets/images/paper-plane-top.svg"
                        height="14px"
                        alt=""
                      />

                      <div class="tooltip">Submit</div>
                    </div>
                  </div>

                  <div>
                    <div class="expanded-item">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/newspaper.svg" height="20px" alt="" />
                        <p>Source</p>
                      </div>

                      <div class="switcher">
                        <div
                          @click="switchMainView('news')"
                          :class="{ activeswitch: mainView === 'news' }"
                          class="switch-item"
                        >
                          News
                        </div>
                        <div
                          @click="switchMainView('social')"
                          :class="{ activeswitch: mainView === 'social' }"
                          class="switch-item"
                        >
                          X
                        </div>
                        <div
                          @click="switchMainView('instagram')"
                          :class="{ activeswitch: mainView === 'instagram' }"
                          class="switch-item"
                        >
                          IG
                        </div>
                        <div
                          @click="switchMainView('website')"
                          :class="{ activeswitch: mainView === 'website' }"
                          class="switch-item"
                        >
                          URL
                        </div>
                        <div
                          @click="switchMainView('pdf')"
                          :class="{ activeswitch: mainView === 'pdf' }"
                          class="switch-item"
                        >
                          PDF
                        </div>
                      </div>
                    </div>

                    <div class="expanded-item">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/calendar.svg" height="18px" alt="" />
                        <p>Date Range</p>
                      </div>

                      <div>
                        <input
                          disabled
                          class="area-input-smallest"
                          type="date"
                          v-model="dateStart"
                        />
                        -
                        <input disabled class="area-input-smallest" type="date" v-model="dateEnd" />
                      </div>
                    </div>

                    <div class="expanded-item-column">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/arrow-trend-up.svg" height="18px" alt="" />
                        <p>Search Examples:</p>
                      </div>

                      <div class="horizontal-padding rows">
                        <p
                          v-for="(example, i) in searchExamples"
                          :key="i"
                          @click="setNewSearch(example)"
                          class="bold gray-title"
                        >
                          {{ example }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div style="padding: 48px 0" v-else>
            <div>
              <div
                style="margin: 2rem 0"
                class="news-container"
                v-for="(tweet, i) in tweets"
                :key="i"
              >
                <div class="news-card-medium">
                  <div class="attachment-header-container">
                    <div>
                      <header>
                        <div class="card-row-med">
                          <img :src="tweet.user.profile_image_url" />
                          <h1
                            @click="openTweet(tweet.user.username, tweet.id)"
                            class="article-title"
                          >
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
                      <span class="divider-dot">.</span>
                      <small class="bold-text"
                        >{{ formatNumber(tweet.user.public_metrics.followers_count) }}
                        <span>Followers</span>
                      </small>
                      <span class="divider-dot">.</span>
                      <span class="off-gray time">{{
                        getTimeDifferenceInMinutes(tweet.created_at)
                      }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style="width: 100%" v-else-if="mainView === 'instagram'">
          <div v-if="loading">
            <div class="small-container">
              <div class="loading">
                <p>Gathering posts</p>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </div>
          </div>

          <div style="padding-top: 2rem" v-else-if="!(posts && posts.length)">
            <div
              style="width: 100%; padding: 0 32px; padding-top: 16px"
              class="small-container letter-spacing"
            >
              <div v-if="!selectedSearch" class="text-width">
                <p v-if="hasIgIntegration" style="margin: 0">
                  Get a pulse on whats happening on Instagram
                </p>

                <p style="margin: 0" v-else>
                  Start by connecting your IG account
                  <span class="link" @click="goToIntegrations">here</span>.
                </p>
              </div>

              <div style="width: 100%; margin-top: 32px">
                <div style="width: 100%" class="large-input-container">
                  <div style="border: none; box-shadow: none" class="input-container">
                    <img
                      class="left-margin-m"
                      src="@/assets/images/search.svg"
                      height="20px"
                      alt=""
                    />
                    <textarea
                      id="search-input"
                      @keyup.enter="generateNewSearch(false)"
                      class="area-input text-area-input"
                      placeholder="Enter hashtag..."
                      autocomplete="off"
                      v-model="newSearch"
                      v-autoresize
                      :disabled="loading || summaryLoading || !hasIgIntegration"
                    />

                    <div
                      @click="generateNewSearch(false)"
                      class="image-container left-margin right-margin-m wrapper"
                      :class="newSearch ? 'dark-blue-bg' : ''"
                    >
                      <img
                        style="margin: 0; cursor: text"
                        src="@/assets/images/paper-plane-top.svg"
                        height="14px"
                        alt=""
                      />

                      <div class="tooltip">Submit</div>
                    </div>
                  </div>

                  <div>
                    <div class="expanded-item">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/newspaper.svg" height="20px" alt="" />
                        <p>Source</p>
                      </div>

                      <div class="switcher">
                        <div
                          @click="switchMainView('news')"
                          :class="{ activeswitch: mainView === 'news' }"
                          class="switch-item"
                        >
                          News
                        </div>
                        <div
                          @click="switchMainView('social')"
                          :class="{ activeswitch: mainView === 'social' }"
                          class="switch-item"
                        >
                          X
                        </div>
                        <div
                          @click="switchMainView('instagram')"
                          :class="{ activeswitch: mainView === 'instagram' }"
                          class="switch-item"
                        >
                          IG
                        </div>
                        <div
                          @click="switchMainView('website')"
                          :class="{ activeswitch: mainView === 'website' }"
                          class="switch-item"
                        >
                          URL
                        </div>
                        <div
                          @click="switchMainView('pdf')"
                          :class="{ activeswitch: mainView === 'pdf' }"
                          class="switch-item"
                        >
                          PDF
                        </div>
                      </div>
                    </div>

                    <div class="expanded-item">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/calendar.svg" height="18px" alt="" />
                        <p>Date Range</p>
                      </div>

                      <div>
                        <input class="area-input-smallest" type="date" v-model="dateStart" />
                        -
                        <input class="area-input-smallest" type="date" v-model="dateEnd" />
                      </div>
                    </div>

                    <div class="expanded-item-column">
                      <div class="row horizontal-padding-s img-text">
                        <img src="@/assets/images/hastag.svg" height="18px" alt="" />
                        <p>Used Hashtags:</p>
                      </div>

                      <div class="horizontal-padding rows max-height">
                        <p
                          @click="setNewSearch(extractHashtag(hashtag))"
                          v-for="(hashtag, i) in usedHashtags"
                          :key="i"
                          class="bold gray-title"
                        >
                          {{ extractHashtag(hashtag) }}
                        </p>
                      </div>

                      <!-- <div style="width: 100%" lass="horizontal-padding rows" v-else>
                        <p class="">hello world</p>
                      </div> -->
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div style="padding: 48px 0" v-else>
            <div>
              <div
                style="margin: 2rem 0"
                class="news-container"
                v-for="(post, i) in posts"
                :key="i"
              >
                <div @click="goToIg(post.permalink)" class="row">
                  <small class="gray-title-no-margin">{{
                    formattedPostDate(post.timestamp)
                  }}</small>
                </div>
                <div class="news-card-medium">
                  <div v-if="post.media_type" class="tweet-attachement">
                    <img
                      v-if="post.media_type === 'IMAGE'"
                      :src="post.media_url"
                      class="cover-photo-ig"
                      alt=""
                    />

                    <video
                      style="margin-top: 1rem"
                      v-else-if="post.media_type === 'VIDEO'"
                      width="400"
                      height="200"
                      controls
                    >
                      <source :src="post.media_url" type="video/mp4" />
                    </video>

                    <div v-else-if="post.media_type === 'CAROUSEL_ALBUM'" class="carousel">
                      <div
                        class="carousel-slide"
                        :style="{ transform: `translateX(-${post.currentIndex * 100}%)` }"
                      >
                        <div
                          v-for="(img, index) in post.children.data"
                          :key="index"
                          class="carousel-item"
                        >
                          <img
                            v-if="img.media_type === 'IMAGE'"
                            :src="img.media_url"
                            class="cover-photo-ig"
                            alt=""
                          />

                          <video
                            style="margin-top: 1rem"
                            v-else-if="img.media_type === 'VIDEO'"
                            width="400"
                            height="200"
                            controls
                          >
                            <source :src="img.media_url" type="video/mp4" />
                          </video>
                        </div>
                      </div>

                      <div class="car-dots">
                        <span
                          v-for="(img, index) in post.children.data"
                          :key="index"
                          class="car-dot"
                          :class="{ active: index === post.currentIndex }"
                          @click="goTo(post, index)"
                        ></span>
                      </div>
                    </div>
                  </div>

                  <div class="attachment-header-container">
                    <div style="margin-top: 16px">
                      <p class="article-preview">{{ post.caption }}</p>
                    </div>
                  </div>

                  <div class="card-footer">
                    <div class="author-time">
                      <!-- <span class="author">{{ '@' + tweet.user.username }}</span> -->

                      <small class="bold-text"
                        >{{ formattedNumber(post.like_count) }}
                        <span>Likes</span>
                      </small>
                      <span class="divider-dot">.</span>
                      <small class="bold-text"
                        >{{ formattedNumber(post.comments_count) }}
                        <span>Comments</span>
                      </small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div style="width: 100%; padding: 32px 0" v-else-if="mainView === 'website'">
          <div v-if="clipLoading">
            <div class="small-container">
              <div class="loading">
                <p>Generating clips</p>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </div>
          </div>

          <div
            class="small-container letter-spacing"
            style="width: 100%; padding: 0 32px; padding-top: 16px"
            v-else-if="!addedArticles.length && !clipLoading"
          >
            <div v-if="!selectedSearch" class="text-width">
              <p style="margin: 0">Summarize an article</p>
            </div>

            <div style="width: 100%; margin-top: 32px">
              <div style="width: 100%" class="large-input-container">
                <div style="border: none; box-shadow: none" class="input-container">
                  <img
                    class="left-margin-m"
                    src="@/assets/images/search.svg"
                    height="20px"
                    alt=""
                  />

                  <textarea
                    @keyup.enter="uploadArticle"
                    class="area-input text-area-input"
                    placeholder="Paste article url..."
                    v-model="uploadLink"
                    :disabled="contentLoading"
                  />

                  <div
                    @click="uploadArticle"
                    class="image-container left-margin right-margin-m wrapper"
                    :class="newSearch ? 'dark-blue-bg' : ''"
                  >
                    <img
                      style="margin: 0; cursor: text"
                      src="@/assets/images/paper-plane-top.svg"
                      height="14px"
                      alt=""
                    />

                    <div class="tooltip">Submit</div>
                  </div>
                </div>

                <div>
                  <div class="expanded-item">
                    <div class="row horizontal-padding-s img-text">
                      <img src="@/assets/images/newspaper.svg" height="20px" alt="" />
                      <p>Source</p>
                    </div>

                    <div class="switcher">
                      <div
                        @click="switchMainView('news')"
                        :class="{ activeswitch: mainView === 'news' }"
                        class="switch-item"
                      >
                        News
                      </div>
                      <div
                        @click="switchMainView('social')"
                        :class="{ activeswitch: mainView === 'social' }"
                        class="switch-item"
                      >
                        X
                      </div>
                      <div
                        @click="switchMainView('instagram')"
                        :class="{ activeswitch: mainView === 'instagram' }"
                        class="switch-item"
                      >
                        IG
                      </div>
                      <div
                        @click="switchMainView('website')"
                        :class="{ activeswitch: mainView === 'website' }"
                        class="switch-item"
                      >
                        URL
                      </div>
                      <div
                        @click="switchMainView('pdf')"
                        :class="{ activeswitch: mainView === 'pdf' }"
                        class="switch-item"
                      >
                        PDF
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-else>
            <div v-for="(article, i) in addedArticles" :key="i" class="news-container">
              <div class="news-card" @click="selectArticle(article)">
                <header>
                  <div class="card-col">
                    <div class="card-top-left">
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
                    <span class="divider-dot">.</span>
                    <span class="off-gray time">{{
                      getTimeDifferenceInMinutes(article.publish_date)
                    }}</span>
                    <span class="divider-dot">.</span>
                  </div>
                  <div class="footer-icon-container">
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
                        <img src="@/assets/images/sparkles-thin.svg" height="14px" alt="" />
                        {{
                          articleSummaryLoading && loadingUrl === article.link
                            ? 'Summarizing'
                            : 'Summarize'
                        }}

                        <div
                          style="margin-left: 4px"
                          v-if="articleSummaryLoading && loadingUrl === article.link"
                          class="loading-small"
                        >
                          <div class="dot"></div>
                          <div class="dot"></div>
                          <div class="dot"></div>
                        </div>
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
                          {{
                            articleSummaryLoading && loadingUrl === article.link
                              ? 'Submitting'
                              : 'Submit'
                          }}

                          <div
                            style="margin-left: 4px"
                            v-if="articleSummaryLoading && loadingUrl === article.link"
                            class="loading-small"
                          >
                            <div class="dot"></div>
                            <div class="dot"></div>
                            <div class="dot"></div>
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style="width: 100%; padding: 32px 0" v-else-if="mainView === 'pdf'">
          <!-- <div v-if="loading">
            <div class="small-container">
              <div class="loading">
                <p>Summarizing PDF</p>
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
              </div>
            </div>
          </div> -->

          <div
            class="small-container letter-spacing"
            style="width: 100%; padding: 0 32px; padding-top: 16px"
          >
            <div class="text-width">
              <!-- <h3 style="margin: 0; font-size: 24px" class="beta-span">
                Research Assistant <span>Beta</span>
              </h3> -->
              <p style="margin: 0" class="beta-span">Summarize a short PDF <span>Beta</span></p>
            </div>

            <div :class="{ opaque: summaryLoading }" style="width: 100%; margin-top: 32px">
              <div style="width: 100%" class="large-input-container">
                <!-- <div style="border: none; box-shadow: none" class="input-container">
                  <img
                    class="left-margin-m"
                    src="@/assets/images/search.svg"
                    height="20px"
                    alt=""
                  />

                  <textarea
                    class="area-input text-area-input"
                    placeholder="Paste PDF url..."
                    v-model="pdfLink"
                    :disabled="loading"
                  />

                  <div
                    class="image-container left-margin right-margin-m wrapper"
                    :class="newSearch ? 'dark-blue-bg' : ''"
                  >
                    <img
                      style="margin: 0; cursor: text"
                      src="@/assets/images/paper-plane-top.svg"
                      height="14px"
                      alt=""
                    />

                    <div class="tooltip">Submit</div>
                  </div>
                </div> -->
                <div style="border-top: none; padding-bottom: 16px" class="expanded-item">
                  <div class="row horizontal-padding-s img-text">
                    <img src="@/assets/images/upload.svg" height="18px" alt="" />

                    <div @click="openFilePicker" class="custom-file-upload">
                      <input
                        :disabled="summaryLoading"
                        @change="handleFileUpload"
                        type="file"
                        accept=".pdf"
                        id="pdfile"
                        ref="fileInput"
                      />
                      <label class="ellipsis-text-s" style="cursor: pointer" for="fileInput">
                        {{ selectedFile ? selectedFile.name : 'Upload PDF' }}
                      </label>

                      <div v-if="selectedFile" class="file-img">
                        <img src="@/assets/images/upload2.svg" height="12px" alt="" />
                      </div>
                    </div>
                  </div>

                  <div
                    @click="summarizePdf"
                    class="image-container left-margin right-margin-m wrapper"
                    :class="{ 'dark-blue-bg': selectedFile, void: summaryLoading }"
                  >
                    <img
                      style="margin: 0"
                      src="@/assets/images/paper-plane-top.svg"
                      height="14px"
                      alt=""
                    />

                    <div class="tooltip">Summarize</div>
                  </div>
                </div>
                <div>
                  <div class="expanded-item">
                    <div class="row horizontal-padding-s img-text">
                      <img src="@/assets/images/pdf.svg" height="20px" alt="" />
                      <p>Source</p>
                    </div>

                    <div class="switcher">
                      <div
                        @click="switchMainView('news')"
                        :class="{ activeswitch: mainView === 'news' }"
                        class="switch-item"
                      >
                        News
                      </div>
                      <div
                        @click="switchMainView('social')"
                        :class="{ activeswitch: mainView === 'social' }"
                        class="switch-item"
                      >
                        X
                      </div>
                      <div
                        @click="switchMainView('instagram')"
                        :class="{ activeswitch: mainView === 'instagram' }"
                        class="switch-item"
                      >
                        IG
                      </div>
                      <div
                        @click="switchMainView('website')"
                        :class="{ activeswitch: mainView === 'website' }"
                        class="switch-item"
                      >
                        URL
                      </div>
                      <div
                        @click="switchMainView('pdf')"
                        :class="{ activeswitch: mainView === 'pdf' }"
                        class="switch-item"
                      >
                        PDF
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="footer sticky-bottom">
        <div class="centered">
          <button
            class="img-button-blue"
            @click="resetAll"
            v-if="
              (filteredArticles && filteredArticles.length) ||
              (tweets && tweets.length) ||
              addedArticles.length ||
              posts.length
            "
          >
            <img src="@/assets/images/search.svg" height="18px" alt="" />
            New Search
          </button>
        </div>
      </div>
    </section>

    <section id="summaries" class="container gray-bg">
      <div v-if="summary" class="header sticky-top padding-top-s gray-bg centered-column">
        <div style="margin-top: 2rem; width: 88%" class="flex-end">
          <div @click="copyText" class="wrapper icon-button white-bg right-margin">
            <img
              style="cursor: pointer"
              class="img-highlight"
              src="@/assets/images/clipboard.svg"
              height="14px"
              alt=""
            />
            <div class="tooltip-below">{{ copyTip }}</div>
          </div>

          <div
            @click="sendSummaryEmail"
            class="wrapper icon-button white-bg right-margin"
            :disabled="sentSummaryEmail"
            v-if="mainView !== 'social' && mainView !== 'website' && mainView !== 'pdf'"
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

            <div v-if="sendSummaryEmailText !== 'Sent!'" class="tooltip-below">Send Email</div>
          </div>

          <div>
            <div
              @click="toggleNotifyModal"
              class="wrapper icon-button white-bg right-margin"
              :disabled="sentSummaryEmail"
              v-if="mainView === 'news' && !notifiedList.includes(searchId)"
            >
              <img
                height="14px"
                src="@/assets/images/bell.svg"
                alt=""
                class="filter-green img-highlight"
                :class="{ dim: !(searchSaved || savedSearch) }"
              />
              <div class="tooltip-below">
                {{ searchSaved || savedSearch ? emailText : 'Save search to enable alerts' }}
              </div>
            </div>

            <div
              @click="removeEmailAlert"
              class="wrapper icon-button white-bg right-margin"
              v-else-if="
                mainView === 'news' &&
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
              <div class="tooltip-below">Disable</div>
            </div>
          </div>

          <button
            class="green-button"
            @click="toggleSaveModal"
            :disabled="
              articleSummaryLoading ||
              loading ||
              summaryLoading ||
              savingSearch ||
              savedSearch ||
              mainView === 'website'
            "
            v-if="(filteredArticles && filteredArticles.length) || tweets.length || posts.length"
          >
            Save
          </button>
        </div>

        <!-- <div style="width: 100%" class="space-between vertical-padding">
          <p class="sub-text">AI-generated summary</p>
          <p>{{ summary.split(' ').length }} words</p>
        </div> -->
      </div>

      <div class="content-body" v-if="summaryLoading">
        <div class="centered-col">
          <div class="loading">
            <p>Generating summary</p>
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
          </div>
        </div>
      </div>

      <div v-else class="content-body">
        <div style="padding-top: 80px" class="news-container" v-if="summary">
          <!-- <div style="width: 100%; padding: 16px 0 0 0" class="space-between">
            <p class="sub-text">AI-generated summary</p>
            <p>{{ summary.split(' ').length }} words</p>
          </div> -->

          <div class="relative">
            <pre
              style="overflow-y: scroll; padding-bottom: 120px"
              v-html="summary"
              class="pre-text"
            ></pre>

            <div v-if="showSummaryMenu" class="summary-section">
              <div style="width: 100%" class="large-input-container">
                <div
                  style="border: none; box-shadow: none; padding-bottom: 0.5rem"
                  class="input-container"
                >
                  <img
                    v-if="
                      (filteredArticles && filteredArticles.length) ||
                      (tweets && tweets.length) ||
                      addedArticles.length
                    "
                    class="left-margin-m blue-icon"
                    style="margin-top: 0"
                    src="@/assets/images/sparkle.svg"
                    height="18px"
                    alt=""
                  />

                  <img
                    v-else
                    class="left-margin-m"
                    src="@/assets/images/sparkles-nofill-round.svg"
                    height="18px"
                    alt=""
                  />

                  <textarea
                    style=""
                    class="area-input text-area-input"
                    placeholder="Summary instructions..."
                    autofocus
                    autocomplete="off"
                    v-model="newTemplate"
                    :disabled="!summary || loading || summaryLoading"
                    v-autoresize
                  />

                  <div
                    v-if="!newTemplate"
                    class="image-container left-margin right-margin-m white-bg wrapper"
                  >
                    <img src="@/assets/images/paper-plane-top.svg" height="14px" alt="" />
                    <div class="tooltip">Submit</div>
                  </div>

                  <div
                    @click="getChatSummary(filteredArticles, newTemplate)"
                    class="image-container left-margin right-margin-m white-bg"
                    v-else-if="mainView === 'news' && newTemplate"
                    :class="newTemplate ? 'dark-blue-bg' : ''"
                  >
                    <img
                      style="margin: 0"
                      src="@/assets/images/paper-plane-full.svg"
                      height="14px"
                      alt=""
                    />
                  </div>

                  <div
                    @click="summarizePdf(newTemplate)"
                    class="image-container left-margin right-margin-m white-bg"
                    v-else-if="mainView === 'pdf' && newTemplate"
                    :class="newTemplate ? 'dark-blue-bg' : ''"
                  >
                    <img
                      style="margin: 0"
                      src="@/assets/images/paper-plane-full.svg"
                      height="14px"
                      alt=""
                    />
                  </div>

                  <div
                    @click="getPostsSummary"
                    class="image-container left-margin right-margin-m white-bg"
                    :class="newTemplate ? 'dark-blue-bg' : ''"
                    v-else-if="mainView === 'instagram'"
                  >
                    <img
                      style="margin: 0"
                      src="@/assets/images/paper-plane-full.svg"
                      height="14px"
                      alt=""
                    />
                  </div>

                  <div
                    @click="getChatSummary(preparedTweets, newTemplate)"
                    class="image-container left-margin right-margin-m white-bg"
                    :class="newTemplate ? 'dark-blue-bg' : ''"
                    v-else-if="newTemplate"
                  >
                    <img
                      style="margin: 0"
                      src="@/assets/images/paper-plane-full.svg"
                      height="14px"
                      alt=""
                    />
                  </div>
                </div>

                <div class="expanded-item-column">
                  <div class="row horizontal-padding-s img-text">
                    <img src="@/assets/images/file-ai.svg" height="18px" alt="" />
                    <p>Templates:</p>
                  </div>

                  <div class="horizontal-padding rows">
                    <p
                      v-for="(example, i) in summaryExamples"
                      :key="i"
                      @click="setNewSummary(example.value)"
                      class="bold gray-title"
                    >
                      {{ example.name }}
                    </p>
                  </div>

                  <div style="width: 100%; margin-top: 16px" class="flex-end small-buttons">
                    <button @click="toggleSummaryMenu">Close</button>

                    <!-- <button v-if="!newTemplate">Submit</button>

                    <button
                      class="blue-button"
                      @click="getChatSummary(filteredArticles, newTemplate)"
                      v-else-if="mainView === 'news' && newTemplate"
                    >
                      Submit
                    </button>

                    <button
                      class="blue-button"
                      @click="getChatSummary(preparedTweets, newTemplate)"
                      v-else-if="newTemplate"
                    >
                      Submit
                    </button> -->
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="centered-col" v-else>
          <div class="image-container white-bg extra-padding">
            <img src="@/assets/images/comment.svg" height="32px" alt="" />
          </div>
          <p>Your summary will appear here.</p>
        </div>
      </div>

      <div class="footer sticky-bottom gray-bg">
        <div class="centered">
          <button @click="toggleSummaryMenu" v-if="summary" class="img-button-blueicon">
            <img src="@/assets/images/sparkle.svg" height="18px" alt="" />
            Provide Summary Instructions
          </button>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { Comms } from '@/services/comms'
import User from '@/services/users'

export default {
  name: 'SearchSummaries',
  components: {
    Modal: () => import(/* webpackPrefetch: true */ '@/components/InviteModal'),
  },
  data() {
    return {
      currentIndex: 0,
      selectedFile: null,
      pdfLoaded: false,
      pdfLink: null,
      showSummaryMenu: false,
      expandedView: false,
      promptModalOpen: false,
      dateOpen: false,
      preparedTweets: null,
      addedClip: false,
      showSummaryInput: true,
      contentType: 'Instructions',
      showSummaryInstructions: true,
      showingViews: false,
      summarizing: false,
      saveModalOpen: false,
      detialText: null,
      detailTitle: null,
      currentAlertId: null,
      alertSet: false,
      emailText: 'Activate Alerts',
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
      posts: [],
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
      chatSummaryLoading: false,
      paidModal: false,
      showingDropdown: false,
      showGenerateDropdown: false,
      selectedOption: null,
      successModal: false,
      errorModal: false,
      selectedSearch: null,
      selectedDateTime: '',
      searchExamples: [
        `"Cancer Research"`,
        `Apple Vision PRO`,
        `Exercise AND TikTok`,
        `Supreme Court AND Social Media`,
        `“Embedded Finance”`,
        `Fashion AND Sustainability`,
      ],
      summaryExamples: [
        {
          name: `Topic Summary`,
          value: `Bring {BrandX} up to speed on what’s happening. Identify what aspects of the topic are most intriguing or concerning to the public. No salutations.`,
        },
        {
          name: `PR Advice`,
          value: `As {BrandX}'s PR agency, provide creative suggestions on how they should respond to or leverage this news`,
        },
        {
          name: `Newsjacking Ideas`,
          value: `Provide creative newsjacking ideas for {BrandX} based on this coverage`,
        },
        {
          name: `Media Pitching`,
          value: `Summarize the news for {BrandX}. Provide creative pitching angles. List 5 journalists (from top pubs, include pitching tips) I can pitch`,
        },
        {
          name: `Find Journalists`,
          value: `List 5 journalists (from top pubs, include pitching tips) I can pitch on behalf of {BrandX}`,
        },
        {
          name: `Media Q&A`,
          value: `List 5 questions & answers journalists would ask {BrandX} leadership team`,
        },
        {
          name: `Expert Q&A`,
          value: `Generate a list of 5 questions that the public might have about this topic and how an expert {ExpertX} would respond to them.`,
        },
        {
          name: `Pitch Expert`,
          value: `Bring {BrandX} up to speed on what’s happening in terms of {TopicX}. Identify what aspects of the topic are most intriguing or concerning to the public. Identify which of their industry expects could be pitched to the media. No salutations.`,
        },
        {
          name: `Media Analysis`,
          value: `{Brand X} was mentioned in all of these news articles. As the VP of PR, please provide a media dashboard analyzing all the media coverage. Include the following Metrics: Overall Sentiment, Total Potential Reach (estimate a number), Top Stories, Top 10 Outlets (based on assumed circulation, include circulation number and author).`,
        },
        {
          name: `Crisis Comms`,
          value: `IF there is a negative story about {BrandX} or a potential crisis is brewing, then flag the story (headline, source, author, date using mm/dd format) and draft a short crisis communication statement, and suggest 2-3 key messages for damage control. If there is crisis, simply reply with {All good, no crisis :)}`,
        },
        {
          name: `Competitor Update`,
          value: `Bring {BrandX} up to speed on what {CompetitorX} is up to and why it matters, in paragraph form. Only flag the most impactful stories.  One short paragraph for positive and another for negative stories (headline, source, author, date in mm/dd format). Lastly offer 2-3 super creative newsjacking ideas.`,
        },
        {
          name: `Issue Statement`,
          value: `Issue a statement on behalf of {BrandX}`,
        },
        {
          name: `Blog Post`,
          value: `Draft an informative blog post based on this coverage for {BrandX}`,
        },
        {
          name: `SEO Suggestions`,
          value: `Provide top 10 SEO suggestions relating to this topic for {BrandX}`,
        },
        {
          name: `Sales Meeting`,
          value: `I am a sales rep, you are the VP of Sales, bring me up to speed on whats happening in the industry and how I can leverage it to sell my product: {ProductX} -- provide super specific, tangible, and creative advice.`,
        },
        {
          name: `Email Roundup`,
          value: `Craft an email roundup for {BrandX} leadership team bringing them up to speed on the most important, relevant, impactful news. Offer advice at the end. Be short, direct, to the point. No fluff.`,
        },
      ],
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
        `What is the PR impact of this coverage`,
        `Find me the most positive / negative article`,
        'Analyze the media to identify what aspects of the topic are most intriguing or concerning to the public.',
        `Generate a list of 5 questions that the public might have about this topic and how an expert in the field would respond to them.`,
        `Provide top 10 SEO phrases relating to this topic`,
        `Provide creative newsjacking ideas for XXX based on this coverage`,
        `Provide new pitching angles for XXX based on this news`,
        `Provide a comprehensive media monitoring insight dashboard (list top sources, estimate the potential reach, sentiment analysis, competitor highlights, etc.)`,
        `List 5 of the most important headlines (include source name + journalist)`,
        `List 5 journalists (from top pubs, include pitching tips) I can pitch on behalf of XXX`,
        `List 5 questions & answers journalists would ask about XXX`,
        `Issue a statement on behalf of XXX`,
        `Write a blog post based on this coverage`,
      ],
      promptSuggestions: [
        `"Coca-Cola"`,
        `"Commercial real estate" AND "Technology"`,
        `"OpenAI" OR "Google Bard"`,
        `"Apple no stock related news"`,
      ],
    }
  },
  created() {
    this.addedClips = this.$store.state.currentReportClips
    this.shouldCancel = false

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
  },
  beforeDestroy() {
    window.removeEventListener('scroll', this.checkScroll)
    this.abortFunctions()
  },
  methods: {
    goTo(post, index) {
      const postIndex = this.posts.findIndex((p) => p === post)
      if (postIndex !== -1) {
        this.$set(this.posts[postIndex], 'currentIndex', index)
        this.$forceUpdate()
      }
    },
    goToIg(link) {
      window.open(link, '_blank')
    },
    removeHashtags() {
      this.newSearch = this.newSearch.replace(/#/g, '')
    },
    formattedPostDate(timestamp) {
      const dateObj = new Date(timestamp)

      const month = dateObj.getMonth() + 1
      const day = dateObj.getDate()
      const year = dateObj.getFullYear()

      const formattedMonth = month < 10 ? '0' + month : month
      const formattedDay = day < 10 ? '0' + day : day

      const formattedDate = `${formattedMonth}-${formattedDay}-${year}`

      return formattedDate
    },
    formattedNumber(number) {
      if (number) {
        let numStr = number.toString()
        return numStr.replace(/\B(?=(\d{3})+(?!\d))/g, ',')
      } else {
        return 0
      }
    },
    extractHashtag(hashtag) {
      const parts = hashtag.split(/[.\n]/)
      return parts[0]
    },
    openFilePicker() {
      if (!this.summaryLoading) {
        this.$refs.fileInput.click()
      }
    },

    async summarizePdf(instructions) {
      if (!this.selectedFile) {
        console.log('select file first')
        return
      }
      this.summaryLoading = true
      this.showingPromptDropdown = false
      this.showSummaryMenu = false
      try {
        let formData = new FormData()
        formData.append('instructions', instructions ? instructions : 'Summarize the data')
        if (this.selectedFile && this.selectedFile instanceof File) {
          formData.append('pdf_file', this.selectedFile)
        } else {
          console.error('This is not a File object')
        }
        await Comms.api.summarizePDF(formData).then((res) => {
          this.summary = res.content
        })
      } catch (e) {
        // `${e.data.error}`

        this.$toast(`Unable to process. PDF too long or text not readable.`, {
          timeout: 3500,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        // this.selectedFile = null
        this.summaryLoading = false
      }
    },
    handleFileUpload(event) {
      this.summary = ''
      this.selectedFile = event.target.files[0]
    },
    // in case we need file type verification on the server
    uploadPDF() {
      if (!this.selectedFile) {
        console.log('No file selected')
        return
      }
      const formData = new FormData()
      formData.append('pdfFile', this.selectedFile)

      axios
        .post('uploadEndpoint', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        })
        .then((response) => {
          console.log('File uploaded successfully', response.data)
        })
        .catch((error) => {
          console.error('Error uploading file', error)
        })
    },
    toggleSummaryMenu() {
      this.showSummaryMenu = !this.showSummaryMenu
    },
    setNewSearch(txt) {
      this.newSearch = txt
    },
    setNewSummary(txt) {
      this.newTemplate = txt
    },
    togglePromptModal() {
      this.promptModalOpen = !this.promptModalOpen
    },
    selectPrompt(prompt) {
      this.newTemplate = prompt
      this.togglePromptModal()
    },
    toggleDateDropdown() {
      this.dateOpen = !this.dateOpen
    },
    goToIntegrations() {
      this.$router.push({ name: 'PRIntegrations' })
    },
    toggleSaveModal() {
      this.saveModalOpen = !this.saveModalOpen
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
        this.emailText = 'Activate Alerts'
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
        if (val) {
          this.contentInstructions = `Create a ${val} for XXX, newsjacking this article`
        }

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
      this.resetAll()
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      this.clipLoading = true
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
      this.addedArticles = []
      this.tweets = []
      this.posts = []
      this.metaData = { clips: [] }
      this.changeSearch(null)
      this.$store.dispatch('setSearch', null)
      this.summary = ''
      this.tweetError = ''
      this.showSummaryMenu = false
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
      this.mainView =
        search.search_boolean === 'Ig'
          ? 'instagram'
          : search.type === 'SOCIAL_MEDIA'
          ? 'social'
          : 'news'
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
    closeDropDowns() {
      if (this.dateOpen) {
        this.toggleDateDropdown()
      }
    },
    toggleDropdowns() {
      this.expandedView = !this.expandedView
    },
    async generateNewSearch(saved = false, boolean = '') {
      this.filteredArticles = []
      this.tweets = []
      this.changeSearch(null)
      this.savedSearch = null
      this.showGenerateDropdown = false
      this.showingDropdown = false
      this.showSummaryMenu = false
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
        this.getTweets(saved)
      } else if (this.mainView === 'instagram') {
        this.closeRegenModal()
        this.removeHashtags()
        this.getPosts(saved)
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
      this.showingPromptDropdown = false
      this.showSummaryMenu = false
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        let response
        this.summary = ''
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
        this.refreshUser()
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
      this.selectedSearch = search
    },
    async createSearch() {
      this.showSaveName = false
      this.savingSearch = true
      try {
        const response = await Comms.api
          .createSearch({
            name: this.searchName,
            input_text: this.newSearch,
            search_boolean: this.booleanString || 'Ig',
            instructions: this.newTemplate ? this.newTemplate : this.newSearch,
            meta_data: this.metaData,
            type: this.mainView === 'news' ? 'NEWS' : 'SOCIAL_MEDIA',
          })
          .then((response) => {
            if (response.id) {
              this.searchId = response.id
              this.savedSearch = {
                name: response.name,
                input_text: this.newSearch,
                meta_data: this.metaData,
                search_boolean: this.booleanString,
                instructions: this.newTemplate ? this.newTemplate : this.newSearch,
              }

              this.$toast('Search Saved', {
                timeout: 2000,
                position: 'top-left',
                type: 'success',
                toastClassName: 'custom',
                bodyClassName: ['custom'],
              })
            }
          })
      } catch (e) {
        console.log(e)
      } finally {
        this.$store.dispatch('getSearches')

        setTimeout(() => {
          this.saveModalOpen = false
          this.savingSearch = false
          this.successToggle()
        }, 2000)
      }
    },
    successToggle() {
      this.showUpdateBanner = true
      setTimeout(() => {
        this.showUpdateBanner = false
      }, 2000)
    },
    async sendSummaryEmail() {
      this.sendingSummaryEmail = true
      try {
        this.sentSummaryEmail = true

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
    async getTweets(saved = false) {
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
              this.getTweetSummary()
            }

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
        this.refreshUser()
        this.loading = false
      }
    },
    async getPosts(saved = false) {
      this.summary = null
      this.loading = true
      this.changeSearch({ search: this.newSearch, template: this.newTemplate })
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        await Comms.api
          .getPosts({
            hashtag: this.newSearch,
            user_id: this.user.id,
            date_from: this.dateStart,
            date_to: this.dateEnd,
          })
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            console.log(response)
            if (response.posts.length) {
              this.posts = response.posts
                .slice()
                .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))

              this.posts.forEach((post) => {
                post.currentIndex = 0
              })

              this.getPostsSummary()
            }
            this.showingDropdown = false
          })
      } catch (e) {
        console.log(e)
        this.$toast(`${e.data.error}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
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
    prepareIgSummary(posts) {
      let postList = []
      for (let i = 0; i < posts.length; i++) {
        postList.push(
          'Date: ' + posts[i].timestamp + ' Caption:' + posts[i].caption,
          // 'likes: ' +
          // posts[i].likes_count +
        )
      }
      return postList
    },
    getArticleDescriptions(articles) {
      return articles.map(
        (a) =>
          `Content:${a.description} Date:${a.publish_date}, Source:${a.source.name}, Author:${a.author}`,
      )
    },
    async getTweetSummary(instructions = '') {
      let tweets = this.prepareTweetSummary(this.tweets)
      this.preparedTweets = tweets
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
            if (this.searchSaved) {
              this.updateSearch()
            }
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
      }
    },
    async getPostsSummary(instructions = '') {
      let posts = this.prepareIgSummary(this.posts)
      this.summaryLoading = true
      this.summary = ''
      try {
        if (this.shouldCancel) {
          return this.stopLoading()
        }
        await Comms.api
          .getPostsSummary({
            posts: posts,
            instructions: this.newTemplate,
          })
          .then((response) => {
            if (this.shouldCancel) {
              return this.stopLoading()
            }
            this.summary = response.summary
            if (this.searchSaved) {
              this.updateSearch()
            }
            this.refreshUser()
          })
      } catch (e) {
        console.log('Error in getTweetSummary', e)
        this.$toast(`Error: ${e}`, {
          timeout: 2000,
          position: 'top-left',
          type: 'error',
          toastClassName: 'custom',
          bodyClassName: ['custom'],
        })
      } finally {
        this.summarizing = true
        this.summaryLoading = false
        this.showSummaryMenu = false
      }
    },
    async getChatSummary(clips, instructions = '') {
      this.chatSummaryLoading = true
      this.showingPromptDropdown = false
      this.showSummaryMenu = false
      try {
        if (this.mainView === 'news') {
          await this.getSummary(clips, instructions)
        } else if (this.mainView === 'social') {
          await this.getSummary(clips, instructions, true)
        } else if (this.mainView === 'social') {
        } else {
          await this.getSourceSummary()
        }
      } catch (e) {
        console.log('error in getChatSummary', e)
      }
      this.chatSummaryLoading = false
    },
    async getSummary(clips, instructions = '', twitter = false) {
      let allClips
      if (!twitter) {
        allClips = this.getArticleDescriptions(clips)
      } else {
        allClips = clips
      }

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
        this.refreshUser()
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
    selectArticle(article) {
      this.$store.dispatch('updateSelectedArticle', article)
    },
    goToArticle(link) {
      window.open(link, '_blank')
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
    usedHashtags() {
      if (this.user.instagramAccountRef && this.user.instagramAccountRef.hashtagList) {
        return this.user.instagramAccountRef.hashtagList
      } else {
        return []
      }
    },
    hasTwitterIntegration() {
      return !!this.$store.state.user.hasTwitterIntegration
    },
    hasIgIntegration() {
      return !!this.$store.state.user.hasInstagramIntegration
    },
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
    isMobile() {
      return window.innerWidth <= 600
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
      if (!this.newTemplate) return this.searchSuggestions
      return this.searchSuggestions.filter((suggestions) =>
        suggestions.toLowerCase().includes(this.newTemplate.toLowerCase()),
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

.link {
  border-bottom: 1px solid $dark-black-blue;
  padding-bottom: 2px;
  cursor: pointer;
}

.dropdownBorder {
  color: white !important;
  border-radius: 4px;
  background-color: $dark-black-blue;
  font-size: 12px;
  font-family: $thin-font-family;
  padding: 7.5px !important;
}

.date-dropdown {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 1rem;
  position: absolute;
  bottom: 64px;
  right: 0;
  background: white;

  input {
    margin-top: 1rem;
  }
}

.nav-text {
  font-weight: 400;
  font-family: $thin-font-family !important;
  color: #6b6b6b;
  font-size: 13px;
  padding: 6px 0;
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

.col {
  display: flex;
  flex-direction: column;
}

.blue-button {
  @include dark-blue-button();
  background-color: $dark-black-blue !important;
  color: white !important;
  padding: 8px 12px;
  font-size: 14px;
  border: none;
  margin-left: 0;
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

.opaque {
  opacity: 0.75;
}

.img-button {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 12px 32px;
  border-radius: 12px;
  color: $dark-black-blue;
  font-size: 16px;
  img {
    filter: invert(40%);
    margin-right: 8px;
  }
}

.img-button-blueicon {
  @include dark-blue-button();
  background-color: white;
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 12px 32px;
  border-radius: 12px;
  color: $dark-black-blue;
  font-size: 16px;
  img {
    filter: invert(22%) sepia(32%) saturate(554%) hue-rotate(161deg) brightness(99%) contrast(90%);
    margin-right: 8px;
  }
}

.blue-icon {
  filter: invert(22%) sepia(32%) saturate(554%) hue-rotate(161deg) brightness(99%) contrast(90%) !important;
}

.img-button-blue {
  @include dark-blue-button();
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  padding: 12px 32px;
  border-radius: 12px;
  font-size: 16px;
  img {
    filter: invert(100%);
    margin-right: 8px;
  }
}

.icon-button {
  @include dark-blue-button();
  padding: 7px 12px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  img {
    filter: invert(40%);
  }
}

.green-button {
  @include dark-blue-button();
  background-color: $dark-green;
  padding: 8px 16px;
  border: none;
  margin-right: 0;
}

.wrapper {
  display: flex;
  align-items: center;
  font-family: $thin-font-family;
  font-size: 14px;
  position: relative;
  text-align: center;
  -webkit-transform: translateZ(0); /* webkit flicker fix */
  -webkit-font-smoothing: antialiased; /* webkit text rendering fix */
}

.wrapper .tooltip,
.wrapper .tooltip-wide {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  bottom: 100%;
  color: #fff;
  display: block;
  left: -34px;
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

.wrapper .tooltip-below {
  z-index: 10000;
  background: $dark-black-blue;
  border-radius: 4px;
  top: 150%;
  color: #fff;
  display: block;
  left: -30px;
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
  width: 150px !important;
  left: -60px !important;
}

.wrapper .tooltip:before,
.wrapper .tooltip-wide:before {
  bottom: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip-below:before {
  top: -20px;
  content: ' ';
  display: block;
  height: 20px;
  left: 0;
  position: absolute;
  width: 100%;
}

.wrapper .tooltip:after,
.wrapper .tooltip-wide:after {
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

.wrapper .tooltip-below:after {
  border-left: solid transparent 10px;
  border-right: solid transparent 10px;
  border-bottom: solid $dark-black-blue 10px;
  top: -10px;
  content: ' ';
  height: 0;
  left: 50%;
  margin-left: -13px;
  position: absolute;
  width: 0;
}

.wrapper:hover .tooltip,
.wrapper:hover .tooltip-wide,
.wrapper:hover .tooltip-below {
  opacity: 1;
  pointer-events: auto;
  -webkit-transform: translateY(0px);
  -moz-transform: translateY(0px);
  -ms-transform: translateY(0px);
  -o-transform: translateY(0px);
  transform: translateY(0px);
}

.lte8 .wrapper .tooltip,
.lte8 .wrapper .tooltip-wide,
.lt38 .wrapper .tooltip-below {
  display: none;
}

.lte8 .wrapper:hover .tooltip,
.lte8 .wrapper:hover .tooltip-wide,
.lte8 .wrapper:hover .tooltip-below {
  display: block;
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
}

.article-copy-container {
  height: 20px;
  margin-top: 0.5rem;
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
}

.author-time {
  display: flex;
  align-items: center;
  color: $light-gray-blue;
}

.off-gray {
  color: #6b6b6b;
}

.relative {
  position: relative;
}
.absolute {
  position: absolute;
}
.regenerate-article {
  margin-top: 1rem;
}

button {
  font-family: $thin-font-family !important;
}

button:disabled {
  background-color: $off-white !important;
  border: 1px solid rgba(0, 0, 0, 0.1) !important;
}

.tertiary-button {
  @include dark-blue-button();
  padding: 8px 12px !important;
  border: 1px solid rgba(0, 0, 0, 0.2);
  color: $dark-black-blue;
  background-color: white;
  svg,
  img {
    // filter: invert(100%) sepia(10%) saturate(1666%) hue-rotate(162deg) brightness(92%) contrast(90%);
    margin-right: 8px;
  }
}

.letter-spacing {
  //   letter-spacing: 0.25px;
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

.divider-dot {
  position: relative;
  bottom: 0.2rem;
}

.time {
  //   @media only screen and (max-width: 600px) {
  //     max-width: 100px;
  //     font-size: 10px !important;
  //   }
}

.news-container {
  padding: 0 40px;
}

.summary-section {
  position: absolute;
  top: 0;
  z-index: 1000;
  background-color: white;
}

.scroll-container {
  overflow-y: scroll;
}

.scroll-container::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.scroll-container::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.news-card {
  position: relative;
  min-height: 200px;
  width: 100%;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
  padding: 1rem 0;
  margin-bottom: 1rem;

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
  }
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
  }
}

.card-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
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
  font-size: 14px;
  img {
    height: 12px;
    margin-right: 0.5rem;
  }
}
.cover-photo {
  height: 96px;
  width: 100px;
  margin-left: 0.5rem;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: pointer;

  &:hover {
    opacity: 0.7;
  }

  @media only screen and (max-width: 600px) {
    margin-left: 0;
    margin-bottom: 4px;
  }
}

.cover-photo-ig {
  height: 250px;
  width: auto;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;
}

.cover-photo-no-l-margin {
  height: 96px;
  width: 100px;
  margin-top: 1.25rem;
  object-fit: cover;
  cursor: text;
  border-radius: 4px;
}

.article-title {
  font-size: 17px;
  font-weight: 900;
  line-height: 24px;
  letter-spacing: 0;
  color: $base-gray;
  margin: 12px 0;
  max-width: 450px;
  white-space: nowrap;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  cursor: pointer;

  &:hover {
    color: #6b6b6b;
  }

  @media only screen and (max-width: 600px) {
    font-size: 14px;
    max-width: 320px;
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
    max-width: 360px;
  }
}

.article-preview {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 14px;
  height: 52px;
  line-height: 24px;
  display: inline;
  text-overflow: ellipsis;
  overflow: hidden;
  font-weight: 400;
  margin: 0;

  @media only screen and (max-width: 600px) {
    font-size: 13px;
    max-width: 320px;
  }

  @media only screen and (min-width: 1025px) and (max-width: 1300px) {
    max-width: 360px;
  }
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

  span {
    font-size: 12px;
    margin-right: 0.5rem;
  }

  @media only screen and (max-width: 510px) {
    flex-direction: column;
    align-items: flex-start;
    justify-content: flex-start;

    button {
      margin-top: 1.5rem;
      margin-left: 0 !important;
      width: 40vw;
    }
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.footer-icon-container {
  display: flex;
  align-items: center;
}

.small-photo {
  height: 28px;
  width: 28px;
  margin-bottom: 8px;
  object-fit: cover;
  cursor: text;
  border-radius: 100%;
}

.ellipsis-text-s {
  display: inline-block;
  max-width: 200px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;

  // @media only screen and (max-width: 600px) {
  //   max-width: 320px;
  // }

  // @media only screen and (min-width: 601px) and (max-width: 1024px) {
  // }
}

.ellipsis-text {
  max-width: 400px;
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;

  @media only screen and (max-width: 600px) {
    max-width: 320px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.pre-text {
  color: $base-gray;
  font-family: $thin-font-family;
  font-size: 16px;
  line-height: 32px;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.search {
  color: $dark-black-blue;
}

.filtered-blue {
  filter: invert(20%) sepia(28%) saturate(811%) hue-rotate(162deg) brightness(94%) contrast(81%);
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

.loading {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 1.5rem 0;

  p {
    margin-right: 8px;
  }
}

.loading-small {
  display: flex;
  align-items: center;
  border-radius: 6px;
  padding: 0;
}

.right-arrow-footer {
  padding: 2px 0;
  height: 20px;
  margin-left: 1rem;
  cursor: text;
}

h3 {
  font-size: 20px;
  margin: 0;
}

li {
  margin-top: 8px;
}

.bold {
  font-family: $base-font-family;
}

.gray-title {
  width: fit-content;
  border-radius: 4px;
  padding: 2px 6px;
  background-color: $off-white;
  margin-top: 0;
  margin-left: 8px;
  cursor: pointer;
}

.gray-title-no-margin {
  width: fit-content;
  border-radius: 4px;
  padding: 3px 8px;
  background-color: $soft-gray;
  margin-top: 0;
  cursor: pointer;
}

.no-margins {
  // padding-left: 16px;
  p {
    margin: 0;

    img {
      transform: rotate(180deg);
      transform: scaleX(-1);
      margin-right: 2px;
    }
  }
}
.small-container {
  padding-left: 42px;
  padding-right: 32px;
  font-size: 16px !important;
  line-height: 1.75;
}

.beta-span {
  span {
    background-color: $white-blue;
    color: black;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 4px;
  }
}

.blue-filter {
  filter: brightness(0) invert(23%) sepia(19%) saturate(984%) hue-rotate(162deg) brightness(92%)
    contrast(87%);
}

.row {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.rows {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex-wrap: wrap;
  gap: 4px 24px;
}

.row-between {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  @media only screen and (max-width: 510px) {
    display: flex;
    flex-direction: column-reverse;
    align-items: flex-start;
    justify-content: flex-start;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}
.content-body {
  display: flex;
  align-items: flex-start;
  justify-content: flex-start;
  overflow-y: scroll;
  scroll-behavior: smooth;
  z-index: 0;
  padding: 56px 32px 0 32px;
  font-size: 16px;
  width: 100%;
  height: 100%;

  @media only screen and (max-width: 600px) {
    padding: 120px 32px 0 16px;
  }
}

.content-body::-webkit-scrollbar {
  width: 6px;
  height: 0px;
}
.content-body::-webkit-scrollbar-thumb {
  background-color: $soft-gray;
  box-shadow: inset 2px 2px 4px 0 rgba(rgb(243, 240, 240), 0.5);
  border-radius: 6px;
}

.extra-padding-top {
  padding-top: 104px;
}

.search {
  font-family: $thin-font-family;
  font-size: 14px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  background-color: white;

  @media only screen and (max-width: 600px) {
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    /* Styles for tablets */
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }

  @media only screen and (min-width: 1025px) {
    /* Styles for desktops */
  }
}

.container {
  width: 50vw;
  height: 100vh;
  position: relative;

  @media only screen and (max-width: 600px) {
    width: 100vw;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    width: 100vw;
  }
}

p {
  font-size: 16px !important;
  @media only screen and (max-width: 600px) {
    font-size: 14px !important;
  }
}

.container:first-of-type {
  border-right: 1px solid rgba(0, 0, 0, 0.1);

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
    border: none;
  }
}

.header {
  padding: 16px 32px;
  width: 100%;
  background-color: white;
  z-index: 2;
}

.bottom-border {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
}

.vertical-padding {
  padding: 1rem 40px;
}

.horiz-padding {
  padding: 0 40px;
}

.top-border {
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.footer {
  padding: 16px 32px 32px 32px;
  width: 100%;
  background-color: white;
  z-index: 2;
}

.sticky-top {
  position: absolute;
  top: 0;
}

.flex-end {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
}

.small-buttons {
  button {
    @include dark-blue-button();
    background-color: white;
    border: 1px solid rgba(0, 0, 0, 0.1);
    padding: 4px 6px;
    color: $dark-black-blue;
    font-size: 14px;
    margin-right: 8px;
  }
}

.padding-top {
  padding-top: 80px;
}

.padding-top-s {
  padding-top: 63.5px;
}

.sticky-bottom {
  position: absolute;
  bottom: 0;
}

.left-margin {
  margin-left: 8px;
}
.left-margin-m {
  margin-left: 12px;
}

.right-margin {
  margin-right: 8px;
}
.right-margin-m {
  margin-right: 12px;
}

.bottom-margin-xl {
  margin-bottom: 32px;
}

.text-width {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;

  p {
    font-size: 18px;
  }
}

.bottom-border-light {
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);
  padding-bottom: 1rem;
}

.extra-padding {
  padding: 12px !important;
}

.centered {
  display: flex;
  align-items: center;
  justify-content: center;
}

.centered-column {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.centered-col {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  font-size: 16px;
  width: 100%;
  height: 80%;
}

.gray-bg {
  background-color: $off-white;
}

.white-bg {
  background-color: white;
}

.lightblue-bg {
  background-color: $white-blue;
}

.dark-blue-bg {
  background-color: $dark-black-blue !important;
  img {
    filter: invert(100%) !important;
  }
}

.void {
  cursor: not-allowed !important;
}

.img-text {
  img {
    margin-right: 16px;
    filter: invert(40%);
  }
}

.switcher {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-evenly;
  background-color: $off-white;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 32px;
  padding: 6px 2px;
  width: 60%;
}

.switch-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6px 4px;
  border-radius: 32px;
  width: 100%;
  margin: 0 2px;
  cursor: pointer;
  color: $mid-gray;
  white-space: nowrap;
  font-weight: 400;
  font-size: 14px;
}

.activeswitch {
  background-color: white;
  padding: 6px 4px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  color: $dark-black-blue;
  img {
    filter: none;
  }
}

.image-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  padding: 7px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;

  img {
    filter: invert(40%);
  }
}

.image-container:hover,
.image-container-blue:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.image-container-blue {
  border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  padding: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  background-color: $dark-black-blue;
  transition: all 0.2s;

  img {
    filter: brightness(0) invert(100%);
  }
}

input,
textarea {
  font-size: 16px !important;
}

.large-input-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border-radius: 9px;
  padding: 16px;
}

.input-container {
  border: 1px solid rgba(0, 0, 0, 0.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: box-shadow 0.3s ease;
  padding: 0;
  border-radius: 24px;
  width: 100%;
  color: $base-gray;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-direction: row;

  img {
    filter: invert(40%);
  }
}

.area-input {
  width: 85%;
  margin-bottom: 0.25rem;
  max-height: 250px;
  padding: 0 1.25rem;
  line-height: 1.25;
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
  background-color: transparent;
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

.text-area-input {
  padding-top: 1rem;
}

input,
textarea {
  font-family: $thin-font-family;
}

input::placeholder {
  font-family: $thin-font-family;
}
input:disabled {
  cursor: not-allowed;
}
textarea:disabled {
  cursor: not-allowed;
}
textarea::placeholder {
  font-family: $thin-font-family;
}

.space-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.expanded-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 4px 0;
}

.expanded-item-column {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  flex-direction: column;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  padding: 4px 0;
}

.max-height {
  max-height: 30vh;
  overflow-y: scroll;
}

.custom-file-upload {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  padding: 4px 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
  color: black;
}

.file-img {
  margin-left: 12px;
  background-color: white;
  img {
    top: 12px;
    z-index: 5;
    margin-right: 8px;
  }
}

/* Hide the original file input */
.custom-file-upload input[type='file'] {
  padding: 0;
  margin: 0;
  display: none;
}
// p {
//   font-size: 14px;
// }

.horizontal-padding {
  padding: 0 34px 0 36px;

  @media only screen and (max-width: 600px) {
    padding: 0 16px;
  }

  @media only screen and (min-width: 601px) and (max-width: 1024px) {
  }
}

.horizontal-padding-s {
  padding: 0 16px;
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

.blue-text-bg {
  background: $white-blue;
  padding: 32px 12px 12px 12px;
  border-radius: 4px;
  font-size: 16px;
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
.sticky-header {
  position: sticky;
  top: 0;
}

.paid-item:hover {
  cursor: pointer;
  opacity: 0.4;
}

.paid-center {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.aligned-left {
  align-items: flex-start;
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

.aligned-right {
  justify-content: flex-end;
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

.close-x {
  cursor: pointer;
}

.close-x:hover {
  opacity: 0.4;
}
.inverted {
  filter: invert(100%);
}
.top-right {
  position: absolute;
  top: 8px;
  right: 8px;
}

.carousel {
  position: relative;
  overflow: hidden;
  width: 300px;
  margin-top: 8px;
}

.carousel-slide {
  display: flex;
  transition: transform 0.5s ease;
}

.carousel-item {
  flex: 0 0 auto;
  width: 100%;
  text-align: start;
}

.car-dots {
  margin-top: 8px;
  position: sticky;
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  // background-color: rgba(247, 245, 245, 0.644);
  padding: 3px 0;
  // border: 1px solid rgba(0, 0, 0, 0.1);
  border-radius: 4px;
}

.car-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #ccc;
  margin: 0 5px;
  cursor: pointer;
}

.car-dot.active {
  background-color: $dark-black-blue;
}
</style>