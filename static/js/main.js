// Constants
const BASE_URL = window.location.origin;
const API_ENDPOINTS = {
    SIMULAR_INSS: '/inss/api/simular',
    SIMULAR_PORTABILIDADE: '/inss/api/simular-portabilidade',
    SOLICITAR_PORTABILIDADE: '/inss/api/solicitar-portabilidade-out',
    SIMULAR_REFINANCIAMENTO: '/inss/api/simular-refinanciamento'  // Update this endpoint
};

// Utility Functions
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Form Handlers
function handleNovoEmprestimo() {
    $('#inssForm').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            url: BASE_URL + API_ENDPOINTS.SIMULAR_INSS,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                cpf: $('#cpf').val().replace(/[^\d]/g, ''),
                salary: parseFloat($('#salary').val().replace(/[^\d,]/g, '').replace(',', '.')),
                loan_amount: parseFloat($('#loan_amount').val().replace(/[^\d,]/g, '').replace(',', '.')),
                installments: parseInt($('#installments').val())
            }),
            success: function(response) {
                if (response.success) {
                    const result = response.data;
                    $('#simulationResult').html(`
                        <div class="alert alert-success">
                            <h4>Simulação realizada com sucesso!</h4>
                            <p>Proposta: ${result.proposal_id}</p>
                            <p>Valor da parcela: ${formatarMoeda(result.monthly_payment)}</p>
                            <p>Taxa de juros: ${result.annual_interest_rate}% ao ano</p>
                            <p>Valor total: ${formatarMoeda(result.total_amount)}</p>
                            <p>Número de parcelas: ${result.installments}</p>
                        </div>
                    `);
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Erro ao realizar simulação';
                $('#simulationResult').html(`
                    <div class="alert alert-danger">
                        ${error}
                    </div>
                `);
            }
        });
    });
}

function handlePortabilidade() {
    $('#portabilidadeForm').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            url: API_ENDPOINTS.SIMULAR_PORTABILIDADE,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                cpf: $('#cpf').val().replace(/[^\d]/g, ''),
                current_installment: parseFloat($('#current_installment').val().replace(/[^\d,]/g, '').replace(',', '.')),
                remaining_installments: parseInt($('#remaining_installments').val())
            }),
            success: function(response) {
                if (response.success) {
                    const result = response.data;
                    $('#simulationResult').html(`
                        <div class="alert alert-success">
                            <h4>Simulação de Portabilidade realizada com sucesso!</h4>
                            <p>Proposta: ${result.proposal_id}</p>
                            <p>Nova parcela: ${formatarMoeda(result.monthly_payment)}</p>
                            <p>Taxa de juros: ${result.annual_interest_rate}% ao ano</p>
                            <p>Valor total: ${formatarMoeda(result.total_amount)}</p>
                            <p>Parcelas restantes: ${result.installments}</p>
                        </div>
                    `);
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Erro ao realizar simulação de portabilidade';
                $('#simulationResult').html(`
                    <div class="alert alert-danger">
                        ${error}
                    </div>
                `);
            }
        });
    });
}

function handlePortabilidadeOut() {
    $('#portabilidadeOutForm').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            url: API_ENDPOINTS.SOLICITAR_PORTABILIDADE,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                cpf: $('#cpf').val().replace(/[^\d]/g, ''),
                contract_number: $('#contract_number').val(),
                bank_code: $('#bank_code').val()
            }),
            success: function(response) {
                if (response.success) {
                    const result = response.data;
                    $('#requestResult').html(`
                        <div class="alert alert-success">
                            <h4>Solicitação enviada com sucesso!</h4>
                            <p>Protocolo: ${result.protocol}</p>
                            <p>Status: ${result.status}</p>
                        </div>
                    `);
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Erro ao solicitar portabilidade';
                $('#requestResult').html(`
                    <div class="alert alert-danger">
                        ${error}
                    </div>
                `);
            }
        });
    });
}

function handleRefinanciamento() {
    $('#refinanciamentoForm').on('submit', function(e) {
        e.preventDefault();
        
        $.ajax({
            url: API_ENDPOINTS.SIMULAR_REFINANCIAMENTO,
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                cpf: $('#cpf').val().replace(/[^\d]/g, ''),
                current_installment: parseFloat($('#current_installment').val().replace(/[^\d,]/g, '').replace(',', '.')),
                new_installments: parseInt($('#new_installments').val())
            }),
            success: function(response) {
                if (response.success) {
                    const result = response.data;
                    $('#simulationResult').html(`
                        <div class="alert alert-success">
                            <h4>Simulação de Refinanciamento realizada com sucesso!</h4>
                            <p>Proposta: ${result.proposal_id}</p>
                            <p>Nova parcela: ${formatarMoeda(result.monthly_payment)}</p>
                            <p>Taxa de juros: ${result.annual_interest_rate}% ao ano</p>
                            <p>Valor total: ${formatarMoeda(result.total_amount)}</p>
                            <p>Novas parcelas: ${result.installments}</p>
                        </div>
                    `);
                }
            },
            error: function(xhr) {
                const error = xhr.responseJSON?.error || 'Erro ao realizar simulação de refinanciamento';
                $('#simulationResult').html(`
                    <div class="alert alert-danger">
                        ${error}
                    </div>
                `);
            }
        });
    });
}

// Initialize masks and forms
$(document).ready(function() {
    // Initialize masks
    $('#cpf').mask('000.000.000-00');
    $('.money').mask('#.##0,00', { reverse: true });
    
    // Initialize form handlers based on page
    if ($('#inssForm').length) handleNovoEmprestimo();
    if ($('#portabilidadeForm').length) handlePortabilidade();
    if ($('#portabilidadeOutForm').length) handlePortabilidadeOut();
    if ($('#refinanciamentoForm').length) handleRefinanciamento();
});