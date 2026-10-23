# Advisor tool classification (S-07)

Every tool file in the 15 financial agent folders.

| File | Classification |
|---|---|
| architect_orchestrator/tools/AssessArchitectStage.py | not available |
| architect_orchestrator/tools/GenerateArchitectRoadmap.py | not available |
| architect_orchestrator/tools/RecordArchitectMemory.py | not available |
| arbitrage_scout/tools/ScanVendorPricingArbitrage.py | not available |
| arbitrage_scout/tools/ScoreOpportunityVelocity.py | not available |
| arbitrage_scout/tools/TrackArbitragePipeline.py | not available |
| behavioral_mirror/tools/ClassifyConsumerVsAcquirer.py | not available |
| behavioral_mirror/tools/DetectInvisibleTransaction.py | not available |
| behavioral_mirror/tools/Enforce72HourPauseRule.py | not available |
| behavioral_mirror/tools/GenerateIdentityNotification.py | not available |
| behavioral_mirror/tools/GenerateRecalibrationAlert.py | not available |
| behavioral_mirror/tools/LogBehaviorPattern.py | not available |
| behavioral_mirror/tools/RecordArchitectMemory.py | not available |
| behavioral_mirror/tools/TrackSelfTrustCommitments.py | not available |
| capital_allocator/tools/AllocateCapitalWaterfall.py | reads saved state |
| capital_allocator/tools/CompareReinvestment.py | not available |
| cash_flow_engineer/tools/AssignDollarJobs.py | not available |
| cash_flow_engineer/tools/AutomateStabilityFund.py | not available |
| cash_flow_engineer/tools/CategorizeCashFlowRules.py | not available |
| cash_flow_engineer/tools/Enforce156520Allocation.py | not available |
| cash_flow_engineer/tools/ExecuteDebtSnowballForAssets.py | not available |
| discipline_controller/tools/CalculateCashRunway.py | not available |
| discipline_controller/tools/CreateDisciplineProtocol.py | not available |
| discipline_controller/tools/EnforceProfitFirstAllocation.py | not available |
| discipline_controller/tools/ValidateExpenseAgainstRules.py | not available |
| financial_analyst/tools/AnalyzeCashFlowData.py | not available |
| financial_analyst/tools/CheckSolitudeModeGate.py | not available |
| financial_analyst/tools/GenerateFinancialDashboard.py | not available |
| financial_analyst/tools/GenerateReputationCreditDashboard.py | not available |
| financial_analyst/tools/GenerateSilentDashboard.py | not available |
| financial_analyst/tools/TrackMoneyVelocityDashboard.py | not available |
| legacy_architect/tools/DocumentStepUpInBasis.py | not available |
| legacy_architect/tools/EncryptSovereignVault.py | not available |
| legacy_architect/tools/GenerateGenerationalTransferPlan.py | not available |
| legacy_architect/tools/PlanBuyBorrowDieStrategy.py | not available |
| leverage_strategist/tools/ApplyAssetFormula.py | not available |
| leverage_strategist/tools/ApplyReputationSpreadGate.py | not available |
| leverage_strategist/tools/CalculateSpread.py | not available |
| leverage_strategist/tools/ModelIncomeDensity.py | not available |
| leverage_strategist/tools/ValidateAcquisitionDebt.py | not available |
| opportunity_scanner/tools/UnderwriteSmartMove.py | reads saved state |
| opportunity_scanner/tools/FundMicroInvestmentProject.py | not available |
| opportunity_scanner/tools/ScanInvisibleGaps.py | not available |
| opportunity_scanner/tools/ScoreMoneyVelocity.py | not available |
| opportunity_scanner/tools/TrackVelocityPipeline.py | not available |
| reputation_validator/tools/AuditBehavioralReliability.py | not available |
| reputation_validator/tools/AuditProviderBehavioralTrust.py | not available |
| reputation_validator/tools/AuditProviderSelfTrust.py | not available |
| reputation_validator/tools/EvaluatePressurePerformance.py | not available |
| reputation_validator/tools/ExportPortableReputation.py | not available |
| reputation_validator/tools/GenerateVettingReport.py | not available |
| reputation_validator/tools/MeasureStrategyPersistence.py | not available |
| reputation_validator/tools/ScoreConsistencyOverIntensity.py | not available |
| reputation_validator/tools/ScoreProviderRarity.py | not available |
| reputation_validator/tools/ScoreQuietBuilder.py | not available |
| reputation_validator/tools/ScoreReputationCredit.py | not available |
| reputation_validator/tools/UpdateReputationDashboard.py | not available |
| reputation_validator/tools/VetServiceProvider.py | not available |
| risk_officer/tools/BuildKillCase.py | reads saved state |
| tax_strategist/tools/AuditSelfEmployedDeductions.py | not available |
| tax_strategist/tools/CalculateSelfEmploymentTax.py | not available |
| tax_strategist/tools/GenerateQuarterlyEstimateSchedule.py | not available |
| tax_strategist/tools/RecordArchitectMemory.py | not available |
| wealth_architect/tools/BuildInvestmentPolicyStatement.py | not available |
| wealth_architect/tools/CompareRetirementAccounts.py | not available |
| wealth_architect/tools/ProjectSovereigntyNumber.py | not available |

Count: 66 tool files.
Reads saved state means the tool loads user `default` through `backend.services` and does not accept income, essentials, or fund balance as arguments.
Not available means the file is kept in `tools_held/` so the advisor cannot call it. The web app remains the rulebook.
